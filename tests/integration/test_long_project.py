"""Test suite for longitudinal REDCap Project against real REDCap server"""

# pylint: disable=missing-function-docstring
import os

import pytest

if not os.getenv("REDCAPDEMO_SUPERUSER_TOKEN"):
    pytest.skip(
        "Super user token not found, skipping integration tests",
        allow_module_level=True,
    )


@pytest.mark.integration
def test_is_longitudinal(long_project):
    assert long_project.is_longitudinal


@pytest.mark.integration
def test_export_survey_link(long_project):
    link = long_project.export_survey_link(
        instrument="contact_info", event="enrollment_arm_1", record="1"
    )
    assert link.startswith("https://redcapdemo.vumc.org/surveys/?s=")


@pytest.mark.integration
def test_export_survey_queue_link(long_project):
    link = long_project.export_survey_queue_link(record="1")
    assert link.startswith("https://redcapdemo.vumc.org/surveys/?sq=")


@pytest.mark.integration
def test_export_survey_access_code(long_project):
    code = long_project.export_survey_access_code(
        record="1", instrument="contact_info", event="enrollment_arm_1"
    )
    assert len(code) == 9


@pytest.mark.integration
def test_export_survey_return_code(long_project):
    code = long_project.export_survey_return_code(
        record="1", instrument="contact_info", event="enrollment_arm_1"
    )
    assert len(code) == 8


@pytest.mark.integration
def test_survey_participant_export(long_project):
    data = long_project.export_survey_participant_list(
        instrument="contact_info", event="enrollment_arm_1"
    )
    assert len(data) == 1

    data = long_project.export_survey_participant_list(
        instrument="contact_info", format_type="df", event="enrollment_arm_1"
    )
    assert "email" in data.columns


@pytest.mark.integration
def test_project_info_export(long_project):
    data = long_project.export_project_info()
    assert data["purpose"] == 0


@pytest.mark.integration
def test_users_export(long_project):
    data = long_project.export_users(format_type="df", df_kwargs={"index_col": "email"})
    assert data.index.name == "email"


@pytest.mark.integration
def test_users_import_and_delete(long_project):
    test_user = "pandeharris@gmail.com"
    test_user_json = [{"username": test_user}]
    res = long_project.import_users(test_user_json, return_format_type="csv")

    assert res == "1"

    res = long_project.delete_users([test_user])

    assert res == 1


@pytest.mark.integration
def test_records_export_labeled_headers(long_project):
    data = long_project.export_records(format_type="csv", raw_or_label_headers="label")
    assert "Study ID" in data


@pytest.mark.integration
def test_repeating_export(long_project):
    rep = long_project.export_repeating_instruments_events(format_type="json")

    assert isinstance(rep, list)


@pytest.mark.integration
def test_repeating_export_strictly_enfores_format(long_project):
    with pytest.raises(ValueError):
        long_project.export_repeating_instruments_events(format_type="unsupported")


@pytest.mark.integration
def test_import_export_repeating_forms(long_project):
    for format_type in ["xml", "json", "csv", "df"]:
        rep = long_project.export_repeating_instruments_events(format_type=format_type)
        res = long_project.import_repeating_instruments_events(
            to_import=rep, import_format=format_type
        )
        assert res == 1


@pytest.mark.integration
def test_limit_export_records_forms_and_fields(long_project):
    # only request forms
    records_df = long_project.export_records(
        forms=["demographics", "baseline_data"], format_type="df"
    )
    complete_cols = [col for col in records_df.columns if col.endswith("_complete")]

    assert long_project.def_field in records_df.index.names
    assert complete_cols == ["demographics_complete", "baseline_data_complete"]
    # only request fields
    records_df = long_project.export_records(
        fields=["study_comments"], format_type="df"
    )
    assert long_project.def_field in records_df.index.names
    # request forms and fields
    records_df = long_project.export_records(
        forms=["baseline_data"], fields=["study_comments"], format_type="df"
    )
    complete_cols = [col for col in records_df.columns if col.endswith("_complete")]

    assert long_project.def_field in records_df.index.names
    assert complete_cols == ["baseline_data_complete"]


@pytest.mark.integration
def test_arms_export(long_project):
    response = long_project.export_arms()

    assert len(response) == 2

    arm_nums = [arm["arm_num"] for arm in response]
    arm_names = [arm["name"] for arm in response]

    assert arm_nums == [1, 2]
    assert arm_names == ["Drug A", "Drug B"]


@pytest.mark.integration
def test_arms_import(long_project):
    new_arms = [{"arm_num": 3, "name": "Drug C"}]
    response = long_project.import_arms(new_arms)

    assert response == 1

    # REDCap will not return an Arm unless it has an event associated with it
    # Need to add an event to the newly created Arm
    new_events = [{"event_name": "new_event", "arm_num": "3"}]
    response = long_project.import_events(new_events)

    response = long_project.export_arms()
    assert len(response) == 3

    arm_nums = [arm["arm_num"] for arm in response]
    arm_names = [arm["name"] for arm in response]

    assert arm_nums == [1, 2, 3]
    assert arm_names == ["Drug A", "Drug B", "Drug C"]


@pytest.mark.integration
def test_arms_import_rename(long_project):
    new_arms = [{"arm_num": 1, "name": "Drug Alpha"}]
    response = long_project.import_arms(new_arms)

    assert response == 1

    response = long_project.export_arms()

    assert len(response) == 3

    arm_nums = [arm["arm_num"] for arm in response]
    arm_names = [arm["name"] for arm in response]

    assert arm_nums == [1, 2, 3]
    assert arm_names == ["Drug Alpha", "Drug B", "Drug C"]


@pytest.mark.integration
def test_arms_delete(long_project):
    arms = [3]
    response = long_project.delete_arms(arms)

    assert response == 1

    response = long_project.export_arms()

    assert len(response) == 2

    arm_nums = [arm["arm_num"] for arm in response]
    arm_names = [arm["name"] for arm in response]

    assert arm_nums == [1, 2]
    assert arm_names == ["Drug Alpha", "Drug B"]


@pytest.mark.integration
def test_arms_import_override(long_project):
    # Cache current events, so they can be restored for subsequent tests, because arms, events,
    # and mappings are deleted when the 'override' parameter is used.
    state_dict = {
        "events": long_project.export_events(),
        "form_event_map": long_project.export_instrument_event_mappings(),
    }

    new_arms = [{"arm_num": 3, "name": "Drug C"}]
    response = long_project.import_arms(new_arms)
    assert response == 1
    # Add event for new arm
    new_event = [{"event_name": "new_event", "arm_num": "3"}]
    response = long_project.import_events(new_event)

    response = long_project.export_arms()

    assert len(response) == 3

    new_arms = [{"arm_num": 1, "name": "Drug A"}, {"arm_num": 2, "name": "Drug B"}]
    response = long_project.import_arms(new_arms, override=1)

    assert response == 2

    # Restore project state
    response = long_project.import_events(state_dict["events"])
    assert response == 16

    response = long_project.import_instrument_event_mappings(
        state_dict["form_event_map"]
    )
    assert response == 44

    response = long_project.export_arms()
    assert len(response) == 2

    arm_nums = [arm["arm_num"] for arm in response]
    arm_names = [arm["name"] for arm in response]

    assert arm_nums == [1, 2]
    assert arm_names == ["Drug A", "Drug B"]


@pytest.mark.integration
def test_events_export(long_project):
    response = long_project.export_events()

    assert len(response) == 16


@pytest.mark.integration
def test_events_import(long_project):
    new_events = [{"event_name": "XYZ", "arm_num": "2"}]
    response = long_project.import_events(new_events)

    assert response == 1

    response = long_project.export_events()

    assert len(response) == 17


@pytest.mark.integration
def test_events_delete(long_project):
    events = ["xyz_arm_2"]
    response = long_project.delete_events(events)

    assert response == 1

    response = long_project.export_events()

    assert len(response) == 16


@pytest.mark.integration
def test_export_instruments(long_project):
    response = long_project.export_instruments()
    assert len(response) == 9


@pytest.mark.integration
def test_export_pdf(long_project):
    content, _ = long_project.export_pdf()

    assert isinstance(content, bytes)


@pytest.mark.integration
def test_fem_export(long_project):
    response = long_project.export_instrument_event_mappings()

    assert len(response) == 44


@pytest.mark.integration
def test_fem_import(long_project):
    # Cache current instrument-event mappings, so they can be restored for subsequent tests
    current_fem = long_project.export_instrument_event_mappings()

    instrument_event_mappings = [
        {
            "arm_num": "1",
            "unique_event_name": "enrollment_arm_1",
            "form": "demographics",
        }
    ]
    response = long_project.import_instrument_event_mappings(instrument_event_mappings)
    assert response == 1

    response = long_project.export_instrument_event_mappings()
    assert len(response) == 1

    fem_arm_nums = [fem["arm_num"] for fem in response]
    fem_unique_event_names = [fem["unique_event_name"] for fem in response]
    fem_forms = [fem["form"] for fem in response]

    assert fem_arm_nums == [1]
    assert fem_unique_event_names == ["enrollment_arm_1"]
    assert fem_forms == ["demographics"]

    response = long_project.import_instrument_event_mappings(current_fem)
    assert response == 44
