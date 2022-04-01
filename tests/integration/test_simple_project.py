"""Test suite for simple REDCap Project against real REDCap server"""
# pylint: disable=missing-function-docstring
import os

from io import StringIO

import pandas as pd
import pytest
import semantic_version


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
    assert "create project" in first_log["details"].lower()
