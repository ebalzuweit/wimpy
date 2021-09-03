import configparser
import logging
import os

_data = {}


def _parse_config(config):
    global _data
    _data["DisplayPadding"] = _parse_margin(config["DisplayPadding"])
    _data["WindowMargin"] = _parse_margin(config["WindowMargin"])
    _data["IgnoredClassnames"] = _parse_list(config["IgnoredClassnames"])
    _data["PartitionSplitRatio"] = float(config["PartitionSplitRatio"])


def _parse_margin(margin):
    margins = [int(m) for m in margin.split()]
    if len(margins) < 4:
        return (margins[0], margins[0], margins[0], margins[0])
    else:
        return (margins[0], margins[1], margins[2], margins[3])


def _parse_list(list):
    items = list.split(',')
    return [i.strip() for i in items]


def load_file(filename):
    path = os.path.join(os.getcwd(), filename)
    parser = configparser.ConfigParser()
    parser.read(path)
    _parse_config(parser["Display"])


def display_padding():
    return _data["DisplayPadding"]


def window_margin():
    return _data["WindowMargin"]


def ignored_classnames():
    return _data["IgnoredClassnames"]


def partition_split_ratio():
    return _data["PartitionSplitRatio"]
