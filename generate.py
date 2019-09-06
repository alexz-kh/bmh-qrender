#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import io
import logging as LOG
import os
import shutil
import sys
import tempfile
import traceback
from copy import deepcopy
from distutils.dir_util import copy_tree
from pprint import pformat
import shutil

import jinja2 as test_jinja2
import json
import yaml
from cookiecutter.main import cookiecutter

LOG.basicConfig(level=LOG.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                format='%(asctime)-15s - [%(levelname)s] %(module)s:%(lineno)d: '
                       '%(message)s', )

DEFAULTS = {
    'wf_yaml': os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'defaults.yaml'),
    'contexts_dir': os.path.join(os.path.abspath("."), "contexts"),
    'base_yaml_mask': 'base.'
}


def deepmerge(left, right):
    # Check if any or both of arguments is None
    # * if one of arguments is None
    #  * if left is None return deepcopy(right)
    #  * if right is None return deepcopy(left)
    # * if both are None - return None
    if left is None:
        if right is None:
            return None
        return deepcopy(right)
    elif right is None:
        return deepcopy(left)

    # If both arguments are not None they should be of the same type
    # in order to be merged together.
    if not compare_types(left, right):
        raise Exception("Type mismatch:{} <=> {}".format(left, right))

    if isinstance(left, dict):
        result = {}
        for lkey, lvalue in left.items():
            result[lkey] = deepmerge(lvalue, right.get(lkey))
        for rkey, rvalue in right.items():
            result[rkey] = deepmerge(left.get(rkey), rvalue)
        return result

    if isinstance(left, list):
        result = deepcopy(left)
        result.extend(deepcopy(right))
        return result

    return right


def load_context(fpath):
    with io.open(fpath, encoding='utf-8') as f:
        try:
            return yaml.load(f.read())
        except Exception:
            LOG.error("Unable to load YAML context from file '{}'"
                      .format(fpath), file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def str2bool(v):
    return str(v).lower() not in ('false', '0', '', 'none', 'no', 'n')


def compare_types(left, right):
    left_type = type(left)
    right_type = type(right)
    if left_type != right_type:
        if ((left_type is int and right_type is str and right.isdigit()) or
                (right_type is int and left_type is str and left.isdigit())):
            return True
        elif ((left_type is bool and right_type is str and right in (
                'True', 'False')) or
                  (right_type is bool and left_type is str and left in (
                          'True', 'False'))):
            return True
        return False
    return True


def find_base_context(ctx_src_path):
    for filename in os.listdir(ctx_src_path):
        if os.path.isdir(os.path.join(ctx_src_path, filename)):
            catch = find_base_context(os.path.join(ctx_src_path, filename))
            if catch:
                return catch
        elif filename.startswith(
                DEFAULTS['base_yaml_mask']) and filename.endswith(
            ("yaml", "yml")):
            with open(os.path.join(ctx_src_path, filename)) as f:
                return yaml.load(f.read())


def merge_contexts(ctx_src_dir):
    if os.path.isdir(DEFAULTS['contexts_dir']):
        LOG.warning('removing folder "contexts"')
        shutil.rmtree(DEFAULTS['contexts_dir'])
    os.mkdir(DEFAULTS['contexts_dir'], mode=0o777)

    base_yaml = find_base_context(ctx_src_dir)
    if not base_yaml:
        raise Exception('No base.yml file found!')

    dirs = {ctx_src_dir}
    while len(dirs) > 0:
        current_dir = dirs.pop()
        for filename in os.listdir(current_dir):
            if (os.path.isfile(os.path.join(current_dir, filename)) and
                    not filename.startswith(DEFAULTS['contexts_dir']) and
                    filename.endswith(("yaml", "yml"))):
                f_src = open(os.path.join(current_dir, filename), "r")
                current_yaml = yaml.load(f_src.read())
                result_yaml = deepmerge(base_yaml, current_yaml)
                if current_dir == ctx_src_dir:
                    output_path = DEFAULTS['contexts_dir']
                else:
                    output_path = os.path.join(DEFAULTS['contexts_dir'],
                                               os.path.basename(current_dir))
                if not os.path.exists(output_path):
                    os.mkdir(output_path, mode=0o777)
                f = open(os.path.join(output_path, filename), "w")
                f.write(yaml.dump(result_yaml, default_flow_style=False))
                f.close()
                f_src.close()
            elif os.path.isdir(os.path.join(current_dir, filename)):
                dirs.add(os.path.join(current_dir, filename))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test',
                        action='store_true',
                        help='Test workflow_definition.yml')
    parser.add_argument('-t', '--template',
                        action='append',
                        help='Path(s) to cookiecutter template(s)')
    parser.add_argument('-c', '--config-file',
                        action='append',
                        default=[],
                        help='Path to YAML config file (context)')
    parser.add_argument('-m', '--merge-contexts',
                        action='store_true',
                        help='Merge contexts with base.yml context')
    parser.add_argument('--merge-contexts-dir',
                        default='contexts_src',
                        help='Source directory for merge-contexts action')
    parser.add_argument('-o', '--output-dir',
                        help='Path to output model',
                        default=os.getcwd())
    args = parser.parse_args()

    context = {}
    for f_name in args.config_file:
        if os.path.isfile(f_name):
            context = deepmerge(context, load_context(f_name))
        else:
            LOG.warning("File {} not found!".format(f_name))
    context = context.get('default_context', {})

    if args.merge_contexts:
        if not os.path.exists(os.path.abspath(args.merge_contexts_dir)):
            LOG.error("Wrong merge_contexts_dir value - no such directory")
            sys.exit(1)
        else:
            LOG.info(
                'Attempt to merge contexts on top of contexts/oscore/base.yml')
            merge_contexts(args.merge_contexts_dir)
            sys.exit(0)

    templates = []
    """
    1) Copy whole `template` into tmp folder
    2) Drop disabled components (remove component dir)
    3) Read defaults.yaml['cookiecutter_json'] => save to template/cookiecutter.json
    4) Generate from temp dir to `output-dir`
    5) Delete temp directory.
    """
    tempTemplatesDir = tempfile.mkdtemp(dir=os.getcwd(),
                                        prefix='_temp_')
    templates.append(tempTemplatesDir)
    copy_tree('{0}/template/'.format(os.getcwd()), tempTemplatesDir,
              preserve_symlinks=True)
    componentsDir = os.path.join(tempTemplatesDir)
    # templatesList = os.listdir(componentsDir)
    # for component in templatesList:
    #     comp_dir = os.path.join(componentsDir, component)
    #     # process only dirs
    #     if not os.path.isdir(comp_dir):
    #         continue
    #     # Drop not needed components from generation.
    #     key = "%s_enabled" % component
    #     # infra usually not defined directly, as w-a, we should enabled it
    #     # by default. in case opposite passed.
    #     if key not in context or not str2bool(context[key]):
    #         if str(key) == 'infra_enabled' and key not in context:
    #             LOG.warning('Enable "infra" explicitly')
    #             continue
    #         try:
    #             LOG.warning('Removing component dir: {}'.format(component))
    #             shutil.rmtree(comp_dir)
    #         except OSError as e:
    #             LOG.warning(e)
    #             pass
    # Load defaults, and get cookiecutter.json from it.
    cc_data = load_context(DEFAULTS['wf_yaml'])
    with open(os.path.join(tempTemplatesDir, 'cookiecutter.json'),
              'w') as outfile:
        json.dump(cc_data['cookiecutter_json'], outfile)

    try:
        for template in templates:
            cookiecutter(
                template,
                extra_context=context,
                output_dir=args.output_dir,
                no_input=True,
                overwrite_if_exists=True
            )
    except Exception as e:
        raise
    #shutil.rmtree(tempTemplatesDir)
    #LOG.debug("Directory removed: {}".format(tempTemplatesDir))
