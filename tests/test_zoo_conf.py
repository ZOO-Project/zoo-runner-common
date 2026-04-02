import json

import pytest

from zoo_runner_common.zoo_conf import ResourceRequirement, ZooConf, ZooInputs, ZooOutputs


class TestResourceRequirement:
    def test_from_dict_basic(self):
        rr = ResourceRequirement.from_dict({"coresMin": 2, "ramMax": 4096})
        assert rr.coresMin == 2
        assert rr.ramMax == 4096

    def test_from_dict_ignores_unknown_keys(self):
        rr = ResourceRequirement.from_dict({"coresMin": 1, "unknown_field": "ignored"})
        assert rr.coresMin == 1

    def test_defaults_are_none(self):
        rr = ResourceRequirement()
        assert rr.coresMin is None
        assert rr.ramMax is None
        assert rr.tmpdirMin is None


class TestZooConf:
    def test_extracts_workflow_id(self):
        conf = {"lenv": {"Identifier": "my-workflow", "usid": "abc"}}
        zoo_conf = ZooConf(conf)
        assert zoo_conf.workflow_id == "my-workflow"

    def test_stores_conf_reference(self):
        conf = {"lenv": {"Identifier": "wf", "usid": "123"}}
        zoo_conf = ZooConf(conf)
        assert zoo_conf.conf is conf


class TestZooInputs:
    def test_no_conversion_for_single_occurrence(self):
        inputs = {"param": {"maxOccurs": "1", "value": "hello"}}
        zi = ZooInputs(inputs)
        assert zi.inputs["param"]["value"] == "hello"

    def test_converts_string_to_list_when_max_occurs_gt1(self):
        inputs = {"param": {"maxOccurs": "3", "value": "hello"}}
        zi = ZooInputs(inputs)
        assert zi.inputs["param"]["value"] == ["hello"]

    def test_no_conversion_when_already_list(self):
        inputs = {"param": {"maxOccurs": "3", "value": ["a", "b"]}}
        zi = ZooInputs(inputs)
        assert zi.inputs["param"]["value"] == ["a", "b"]

    def test_get_input_value_returns_value(self):
        inputs = {"x": {"value": "42"}}
        zi = ZooInputs(inputs)
        assert zi.get_input_value("x") == "42"

    def test_get_input_value_raises_key_error_for_missing(self):
        zi = ZooInputs({})
        with pytest.raises(KeyError):
            zi.get_input_value("missing")

    def test_get_processing_parameters_string(self):
        inputs = {"name": {"value": "test"}}
        zi = ZooInputs(inputs)
        assert zi.get_processing_parameters()["name"] == "test"

    def test_get_processing_parameters_integer(self):
        inputs = {"count": {"value": "5", "dataType": "integer"}}
        zi = ZooInputs(inputs)
        result = zi.get_processing_parameters()
        assert result["count"] == 5
        assert isinstance(result["count"], int)

    def test_get_processing_parameters_float(self):
        inputs = {"score": {"value": "3.14", "dataType": "float"}}
        zi = ZooInputs(inputs)
        result = zi.get_processing_parameters()
        assert abs(result["score"] - 3.14) < 1e-6

    def test_get_processing_parameters_boolean(self):
        inputs = {"flag": {"value": "True", "dataType": "boolean"}}
        zi = ZooInputs(inputs)
        result = zi.get_processing_parameters()
        assert result["flag"] is True

    def test_get_processing_parameters_null_value(self):
        inputs = {"opt": {"value": "NULL", "dataType": "string"}}
        zi = ZooInputs(inputs)
        assert zi.get_processing_parameters()["opt"] is None

    def test_get_processing_parameters_list_of_integers(self):
        inputs = {"ids": {"maxOccurs": "5", "value": ["1", "2", "3"], "dataType": ["integer"]}}
        zi = ZooInputs(inputs)
        result = zi.get_processing_parameters()
        assert result["ids"] == [1, 2, 3]

    def test_get_processing_parameters_bbox(self):
        bbox_value = json.dumps([1.0, 2.0, 3.0, 4.0])
        inputs = {
            "bbox": {
                "value": bbox_value,
                "lowerCorner": "1.0 2.0",
                "upperCorner": "3.0 4.0",
                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
            }
        }
        zi = ZooInputs(inputs)
        result = zi.get_processing_parameters()
        assert result["bbox"]["format"] == "ogc-bbox"
        assert result["bbox"]["crs"] == "CRS84"
        assert result["bbox"]["bbox"] == [1.0, 2.0, 3.0, 4.0]

    def test_get_processing_parameters_with_format(self):
        inputs = {"data": {"value": "http://example.com/data.tif", "format": "image/tiff"}}
        zi = ZooInputs(inputs)
        result = zi.get_processing_parameters()
        assert result["data"]["format"] == "image/tiff"
        assert result["data"]["value"] == "http://example.com/data.tif"

    def test_get_processing_parameters_cache_file(self):
        inputs = {"ref": {"value": "s3://bucket/file.tif", "cache_file": "/tmp/cache", "mimeType": "image/tiff"}}
        zi = ZooInputs(inputs)
        result = zi.get_processing_parameters()
        assert result["ref"]["value"] == "s3://bucket/file.tif"
        assert result["ref"]["format"] == "image/tiff"


class TestZooOutputs:
    def test_first_key_becomes_output_key(self):
        outputs = {"result": {"value": None}}
        zo = ZooOutputs(outputs)
        assert zo.output_key == "result"

    def test_empty_outputs_creates_stac_key(self):
        zo = ZooOutputs({})
        assert zo.output_key == "stac"
        assert "stac" in zo.outputs

    def test_get_output_parameters(self):
        outputs = {"out": {"value": "http://example.com/result"}}
        zo = ZooOutputs(outputs)
        assert zo.get_output_parameters() == {"out": "http://example.com/result"}

    def test_set_output(self):
        outputs = {"result": {"value": None}}
        zo = ZooOutputs(outputs)
        zo.set_output("http://example.com/catalog.json")
        assert zo.outputs["result"]["value"] == "http://example.com/catalog.json"

    def test_set_output_on_stac_key_when_empty(self):
        zo = ZooOutputs({})
        zo.set_output("http://example.com/stac.json")
        assert zo.outputs["stac"]["value"] == "http://example.com/stac.json"
