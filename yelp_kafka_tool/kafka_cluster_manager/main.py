from __future__ import absolute_import
from __future__ import unicode_literals

import argparse
import ConfigParser
import logging
from logging.config import fileConfig

from yelp_kafka_tool.kafka_cluster_manager.cmds.decommission import DecommissionCmd
from yelp_kafka_tool.kafka_cluster_manager.cmds.rebalance import RebalanceCmd
from yelp_kafka_tool.kafka_cluster_manager.cmds.stats import StatsCmd
from yelp_kafka_tool.util import config


_log = logging.getLogger()


def parse_args():
    """Parse the arguments."""
    parser = argparse.ArgumentParser(
        description='Alter topic-partition layout over brokers.',
    )
    parser.add_argument(
        '--cluster-type',
        dest='cluster_type',
        help='Type of cluster',
        type=str,
        required=True,
    )
    parser.add_argument(
        '--cluster-name',
        dest='cluster_name',
        help='Name of the cluster (example: uswest1-devc;'
        ' Default to local cluster)',
    )
    parser.add_argument(
        '--discovery-base-path',
        dest='discovery_base_path',
        type=str,
        help='Path of the directory containing the <cluster_type>.yaml config',
    )
    parser.add_argument(
        '--logconf',
        type=str,
        help='Path to logging configuration file. Default: log to console.',
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Proposed-plan will be executed on confirmation.',
    )
    parser.add_argument(
        '--no-confirm',
        action='store_true',
        help='Proposed-plan will be executed without confirmation.'
             ' --apply flag also required.',
    )
    parser.add_argument(
        '--write-to-file',
        dest='proposed_plan_file',
        metavar='<reassignment-plan-file-path>',
        type=str,
        help='Write the partition reassignment plan '
             'to a json file.',
    )

    subparsers = parser.add_subparsers()
    RebalanceCmd().add_subparser(subparsers)
    DecommissionCmd().add_subparser(subparsers)
    StatsCmd().add_subparser(subparsers)

    return parser.parse_args()


def configure_logging(log_conf=None):
    if log_conf:
        try:
            fileConfig(log_conf)
        except ConfigParser.NoSectionError:
            logging.basicConfig(level=logging.INFO)
            _log.error(
                'Failed to load {logconf} file.'
                .format(logconf=log_conf),
            )
    else:
        logging.basicConfig(level=logging.INFO)


def run():
    """Verify command-line arguments and run reassignment functionalities."""
    args = parse_args()

    configure_logging(args.logconf)

    cluster_config = config.get_cluster_config(
        args.cluster_type,
        args.cluster_name,
        args.discovery_base_path,
    )
    args.command(cluster_config, args)
