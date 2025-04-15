"""Test suite for simple REDCap Project against real REDCap server"""

# pylint: disable=missing-function-docstring
import os
import tempfile

from io import StringIO

import pandas as pd
import pytest
import semantic_version

from redcap import RedcapError

if not os.getenv("REDCAPDEMO_SUPERUSER_TOKEN"):
    pytest.skip(
        "Super user token not found, skipping integration tests",
        allow_module_level=True,
    )


@pytest.mark.integration
def test_is_not_longitudinal(simple_project):
    assert not simple_project.is_longitudinal


@pytest.mark.integration
def test_export_records(simple_project):
    proj_records_export = simple_project.export_records()
    assert len(proj_records_export) == 3


@pytest.mark.integration
def test_export_records_always_has_record_id(simple_project):
    proj_records_export = simple_project.export_records(fields=["first_name"])
    assert "record_id" in proj_records_export[0].keys()


@pytest.mark.integration
def test_export_records_df(simple_project):
    proj_records_export = simple_project.export_records(format_type="df")
    assert len(proj_records_export) == 3


@pytest.mark.integration
def test_export_records_df_eav(simple_project):
    proj_records_export = simple_project.export_records(
        format_type="df", record_type="eav"
    )
    assert len(proj_records_export) == 30


@pytest.mark.integration
def test_import_and_delete_records(simple_project):
    new_record_ids = [4, 5, 6]
    test_records = [{"record_id": i} for i in new_record_ids]

    res = simple_project.import_records(test_records)
    assert res["count"] == len(test_records)

    res = simple_project.import_records(test_records, return_content="ids")
    assert len(res) == len(test_records)

    res = simple_project.import_records(test_records, return_content="nothing")
    assert res == [{}]

    res = simple_project.delete_records(new_record_ids)
    assert res == 3


@pytest.mark.integration
@pytest.mark.parametrize(
    ["return_format_type", "import_output", "delete_output"],
    [
        ("csv", "3", "3"),
        ("xml", '<?xml version="1.0" encoding="UTF-8" ?><count>3</count>', "3"),
    ],
)
def test_import_and_delete_records_non_json(
    simple_project, return_format_type, import_output, delete_output
):
    new_record_ids = ["4", "5", "6"]
    test_records_csv = "record_id\n" + "\n".join(new_record_ids)
    test_records_df = pd.read_csv(StringIO(test_records_csv))

    res = simple_project.import_records(
        test_records_df, import_format="df", return_format_type=return_format_type
    )
    assert res == import_output

    res = simple_project.delete_records(
        new_record_ids, return_format_type=return_format_type
    )
    assert res == delete_output


@pytest.mark.integration
def test_import_df_no_index(simple_project):
    # declare df_kwargs without specifying index, which returns a df with no index
    proj_records_export = simple_project.export_records(
        format_type="df", df_kwargs={"sep": ","}
    ).convert_dtypes()

    res = simple_project.import_records(proj_records_export, import_format="df")

    assert res["count"] == 3


@pytest.mark.integration
def test_export_version(simple_project):
    version = simple_project.export_version()
    assert version >= semantic_version.Version("12.0.1")


@pytest.mark.integration
def test_export_users(simple_project):
    users = simple_project.export_users()
    # no need to create a test project with more than one user
    assert len(users) == 1
    # any user in this test project would by necessity have API access
    assert users[0]["api_export"] == 1


@pytest.mark.integration
def test_export_user_roles(simple_project):
    user_roles = simple_project.export_user_roles()
    assert len(user_roles) == 1
    assert user_roles[0]["role_label"] == "Example Role"


@pytest.mark.integration
def test_import_delete_user_roles(simple_project):
    new_role = [{"role_label": "New Role"}]

    res = simple_project.import_user_roles(new_role)
    assert res == 1

    new_role_id = simple_project.export_user_roles()[-1]["unique_role_name"]

    res = simple_project.delete_user_roles([new_role_id])
    assert res == 1


@pytest.mark.integration
def test_export_import_user_role_assignments(simple_project):
    new_user = "pandeharris@gmail.com"
    simple_project.import_users([{"username": new_user}])

    example_role_name = simple_project.export_user_roles()[0]["unique_role_name"]

    res = simple_project.import_user_role_assignment(
        [{"username": new_user, "unique_role_name": example_role_name}]
    )
    assert res == 1

    user_role_assignments = simple_project.export_user_role_assignment()
    test_user_role_name = [
        user_role["unique_role_name"]
        for user_role in user_role_assignments
        if user_role["username"] == new_user
    ][0]
    assert test_user_role_name == example_role_name
    # cleanup
    res = simple_project.delete_users([new_user])
    assert res == 1


@pytest.mark.integration
def test_export_dags(simple_project):
    dags = simple_project.export_dags(format_type="df")

    assert len(dags) == 1


@pytest.mark.integration
def test_import_delete_dags(simple_project):
    new_dag = [{"data_access_group_name": "New DAG", "unique_group_name": ""}]

    res = simple_project.import_dags(new_dag, return_format_type="csv")
    assert res == "1"

    res = simple_project.delete_dags(["new_dag"])
    assert res == 1


@pytest.mark.integration
def test_export_user_dag_assignment(simple_project):
    res = simple_project.export_user_dag_assignment()

    assert len(res) == 1


@pytest.mark.integration
def test_import_user_dag_assignment(simple_project):
    dag_mapping = simple_project.export_user_dag_assignment()
    res = simple_project.import_user_dag_assignment(
        dag_mapping, return_format_type="csv"
    )

    assert res == "1"


@pytest.mark.integration
def test_export_field_names(simple_project):
    field_names = simple_project.export_field_names()
    assert len(field_names) == 16


@pytest.mark.integration
def test_export_one_field_name(simple_project):
    field_names = simple_project.export_field_names(field="first_name")
    assert len(field_names) == 1


@pytest.mark.integration
def test_export_field_names_df(simple_project):
    field_names = simple_project.export_field_names(format_type="df")
    assert all(field_names.columns == ["choice_value", "export_field_name"])


@pytest.mark.integration
def test_export_instruments(simple_project):
    instruments = simple_project.export_instruments()
    assert len(instruments) == 1


@pytest.mark.integration
def test_export_pdf(simple_project):
    content, _ = simple_project.export_pdf()

    assert isinstance(content, bytes)


@pytest.mark.integration
def test_export_and_import_metadata(simple_project):
    original_metadata = simple_project.export_metadata()
    assert len(original_metadata) == 15

    reduced_metadata = original_metadata[:14]
    res = simple_project.import_metadata(reduced_metadata)
    assert res == len(reduced_metadata)
    # then "restore" it (though won't have data for the previously removed fields)
    res = simple_project.import_metadata(original_metadata)
    assert res == len(original_metadata)


@pytest.mark.integration
def test_export_and_import_metadata_csv(simple_project):
    metadata = simple_project.export_metadata("csv")
    assert "field_name,form_name" in metadata
    res = simple_project.import_metadata(to_import=metadata, import_format="csv")
    assert res == 15


@pytest.mark.integration
def test_export_and_import_metadata_df(simple_project):
    metadata = simple_project.export_metadata(
        format_type="df",
        # We don't want to convert these to floats (what pandas does by default)
        # since we need the to stay integers when re-importing into REDCap
        df_kwargs={
            "index_col": "field_name",
            "dtype": {
                "text_validation_min": pd.Int64Dtype(),
                "text_validation_max": pd.Int64Dtype(),
            },
        },
    )
    assert metadata.index.name == "field_name"
    res = simple_project.import_metadata(to_import=metadata, import_format="df")
    assert res == 15


@pytest.mark.integration
def test_export_project_info(simple_project):
    project_info = simple_project.export_project_info()
    assert project_info["is_longitudinal"] == 0


@pytest.mark.integration
def test_export_logging(simple_project):
    logs = simple_project.export_logging(log_type="manage")
    first_log = logs.pop()
    assert "manage/design" in first_log["action"].lower()


@pytest.mark.integration
def test_export_arms(simple_project):
    with pytest.raises(RedcapError):
        simple_project.export_arms()


@pytest.mark.integration
def test_export_events(simple_project):
    with pytest.raises(RedcapError):
        simple_project.export_events()


@pytest.mark.integration
def test_export_instrument_event_mapping(simple_project):
    with pytest.raises(RedcapError):
        simple_project.export_instrument_event_mappings()


@pytest.mark.integration
def test_create_folder_in_repository(simple_project):
    folder_name = "New Folder"
    new_folder = simple_project.create_folder_in_repository(name=folder_name)
    assert new_folder[0]["folder_id"] > 0


@pytest.mark.integration
def test_export_file_repository(simple_project):
    directory = simple_project.export_file_repository()
    assert len(directory) > 0


@pytest.mark.integration
def test_export_file_from_repository(simple_project):
    file_dir = simple_project.export_file_repository()
    text_file = [file for file in file_dir if file["name"] == "test.txt"].pop()
    file_contents, _ = simple_project.export_file_from_repository(
        doc_id=text_file["doc_id"]
    )
    assert isinstance(file_contents, bytes)


@pytest.mark.integration
def test_import_file_repository(simple_project):
    initial_len = len(simple_project.export_file_repository())

    tmp_file = tempfile.TemporaryFile()
    simple_project.import_file_into_repository(
        file_name="new_upload.txt", file_object=tmp_file
    )

    new_len = len(simple_project.export_file_repository())

    assert new_len > initial_len


@pytest.mark.integration
def test_delete_file_from_repository(simple_project):
    file_dir = simple_project.export_file_repository()
    text_file = [file for file in file_dir if file["name"] == "test.txt"].pop()
    resp = simple_project.delete_file_from_repository(doc_id=text_file["doc_id"])
    assert resp == [{}]
