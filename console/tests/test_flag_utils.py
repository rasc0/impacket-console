from console.FlagUtils import flag_to_attr


def test_strips_leading_dashes():
    assert flag_to_attr("-dc-ip") == "dc_ip"
    assert flag_to_attr("--target") == "target"


def test_leaves_bare_positional_names_alone():
    assert flag_to_attr("target") == "target"


def test_prefixes_names_starting_with_a_digit():
    assert flag_to_attr("-6") == "flag_6"


def test_dash_and_underscore_spellings_normalise_to_the_same_attribute():
    assert flag_to_attr("-output-file") == flag_to_attr("output_file")
