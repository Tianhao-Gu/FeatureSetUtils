# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import requests  # noqa: F401
import shutil

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401

from Workspace.WorkspaceClient import Workspace as workspaceService
from FeatureSetUtils.FeatureSetUtilsImpl import FeatureSetUtils
from FeatureSetUtils.FeatureSetUtilsServer import MethodContext
from FeatureSetUtils.authclient import KBaseAuth as _KBaseAuth
from GenomeFileUtil.GenomeFileUtilClient import GenomeFileUtil
from DataFileUtil.DataFileUtilClient import DataFileUtil


class FeatureSetUtilsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('FeatureSetUtils'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'FeatureSetUtils',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.serviceImpl = FeatureSetUtils(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']

        suffix = int(time.time() * 1000)
        cls.wsName = "test_kb_featureset_util_" + str(suffix)
        cls.wsClient.create_workspace({'workspace': cls.wsName})

        cls.gfu = GenomeFileUtil(cls.callback_url)
        cls.dfu = DataFileUtil(cls.callback_url)
        cls.prepare_data()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    @classmethod
    def prepare_data(cls):
        # upload genome object
        genbank_file_name = 'minimal.gbff'
        genbank_file_path = os.path.join(cls.scratch, genbank_file_name)
        shutil.copy(os.path.join('data', genbank_file_name), genbank_file_path)

        genome_object_name = 'test_Genome'
        cls.genome_ref = cls.gfu.genbank_to_genome({'file': {'path': genbank_file_path},
                                                    'workspace_name': cls.wsName,
                                                    'genome_name': genome_object_name
                                                    })['genome_ref']

        # upload differetial expression object
        dem_data = {
            'data': {'col_ids': ['log2_fold_change', 'p_value', 'q_value'],
                     'values': [[3.8118222284877, 0.6, 0.6],
                                [3.3914043515407, 0.6, 0.6],
                                [-4.79258539940901, 0.6, 0.6],
                                [0.6, 0.6, 0.6]],
                     'row_ids': ['AT2G01021.TAIR10', 'AT1G29930.TAIR10',
                                 'AT1G29920.TAIR10', 'AT1G29940.TAIR10']},
            'condition_mapping': {'test_condition_1': 'test_condition_2'},
            'type': 'log2_level',
            'scale': '1.0',
            'genome_ref': cls.genome_ref
        }
        data_type = 'KBaseFeatureValues.DifferentialExpressionMatrix'
        res = cls.dfu.save_objects({'id': cls.dfu.ws_name_to_id(cls.wsName),
                                    'objects': [{'type': data_type,
                                                 'data': dem_data,
                                                 'name': 'test_differetial_expression'}]})[0]
        cls.diff_expression_ref = str(res[6]) + '/' + str(res[0]) + '/' + str(res[4])

        #linear
        dem_data = {
            'data': {'col_ids': ['log2_fold_change', 'p_value', 'q_value'],
                     'values': [[1, 0.6, 0.6],
                                [2, 0.6, 0.6],
                                [0.5, 0.6, 0.6],
                                [0.5, 0.6, 0.6]],
                     'row_ids': ['AT2G01021.TAIR10', 'AT1G29930.TAIR10',
                                 'AT1G29920.TAIR10', 'AT1G29940.TAIR10']},
            'condition_mapping': {'test_condition_1': 'test_condition_2'},
            'type': 'linear',
            'scale': '1.0',
            'genome_ref': cls.genome_ref
        }
        data_type = 'KBaseFeatureValues.DifferentialExpressionMatrix'
        res = cls.dfu.save_objects({'id': cls.dfu.ws_name_to_id(cls.wsName),
                                    'objects': [{'type': data_type,
                                                 'data': dem_data,
                                                 'name': 'test_differetial_expression'}]})[0]
        cls.diff_expression_ref_linear = str(res[6]) + '/' + str(res[0]) + '/' + str(res[4])

        # upload differetial expression set object
        dem_set_data = {
            'items': [{'ref': cls.diff_expression_ref,
                       'label': 'test_condition_1, test_condition_2'},
                      {'ref': cls.diff_expression_ref,
                       'label': 'test_condition_3, test_condition_4'}],
            'description': 'deseq Diff Exp Matrix Set'
        }
        data_type = 'KBaseSets.DifferentialExpressionMatrixSet'
        res = cls.dfu.save_objects({'id': cls.dfu.ws_name_to_id(cls.wsName),
                                    'objects': [{'type': data_type,
                                                 'data': dem_set_data,
                                                 'name': 'test_differetial_expression_matrix_set'}]
                                    })[0]
        cls.diff_expression_set_ref = str(res[6]) + '/' + str(res[0]) + '/' + str(res[4])

        dem_set_data = {
            'items': [{'ref': cls.diff_expression_ref_linear,
                       'label': 'test_condition_1, test_condition_2'},
                      {'ref': cls.diff_expression_ref_linear,
                       'label': 'test_condition_3, test_condition_4'}],
            'description': 'deseq Diff Exp Matrix Set'
        }
        data_type = 'KBaseSets.DifferentialExpressionMatrixSet'
        res = cls.dfu.save_objects({'id': cls.dfu.ws_name_to_id(cls.wsName),
                                    'objects': [{'type': data_type,
                                                 'data': dem_set_data,
                                                 'name': 'test_differetial_expression_matrix_set'}]
                                    })[0]
        cls.diff_expression_set_ref_linear = str(res[6]) + '/' + str(res[0]) + '/' + str(res[4])

        # upload expression matrix object
        expression_matrix_data = {
            'genome_id': cls.genome_ref,
            'scale': 'log2',
            'type': 'level',
            'feature_mapping': {'AT2G01021.TAIR10': 'AT2G01021.TAIR10',
                                'AT1G29930.TAIR10': 'AT1G29930.TAIR10',
                                'AT1G29920.TAIR10': 'AT1G29920.TAIR10',
                                'AT1G29940.TAIR10': 'AT1G29940.TAIR10'},
            'data': {"col_ids": ["test_condition_1",
                                 "test_condition_2"],
                     "row_ids": ['AT2G01021.TAIR10',
                                 'AT1G29930.TAIR10',
                                 'AT1G29920.TAIR10',
                                 'AT1G29940.TAIR10'],
                     "values": [[1, 1],
                                [2, 2],
                                [3, 3],
                                [4, 4]]},
            'condition_mapping': {'test_replicate': 'test_condition_1'}
        }
        data_type = 'KBaseFeatureValues.ExpressionMatrix'
        res = cls.dfu.save_objects({'id': cls.dfu.ws_name_to_id(cls.wsName),
                                    'objects': [{'type': data_type,
                                                 'data': expression_matrix_data,
                                                 'name': 'test_expression_matrix'}]
                                    })[0]
        cls.expression_matrix_ref = str(res[6]) + '/' + str(res[0]) + '/' + str(res[4])

        # upload expression matrix object
        featureset_data = {
            "description": "Generated FeatureSet from DifferentialExpression",
            "element_ordering": [
                "b1",
                "b2",
            ],
            "elements": {
                "b1": [cls.genome_ref],
                "b2": [cls.genome_ref],
            }
        }
        cls.featureset_name = 'test_featureset'
        data_type = 'KBaseCollections.FeatureSet'
        res = cls.dfu.save_objects({'id': cls.dfu.ws_name_to_id(cls.wsName),
                                    'objects': [{'type': data_type,
                                                 'data': featureset_data,
                                                 'name': cls.featureset_name}]
                                    })[0]

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        return self.__class__.wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_bad_upload_featureset_from_diff_expr_params(self):
        invalidate_input_params = {'diff_expression_ref': 'diff_expression_ref',
                                   'p_cutoff': 'p_cutoff',
                                   'q_cutoff': 'q_cutoff',
                                   'fold_scale_type': 'linear',
                                   'fold_change_cutoff': 'fold_change_cutoff',
                                   'workspace_name': 'workspace_name'}
        with self.assertRaisesRegexp(ValueError,
                                     '"fold_scale_type" parameter must be set to "logarithm", if used'):
            self.getImpl().upload_featureset_from_diff_expr(self.getContext(),
                                                            invalidate_input_params)

        invalidate_input_params = {'missing_diff_expression_ref': 'diff_expression_ref',
                                   'p_cutoff': 'p_cutoff',
                                   'q_cutoff': 'q_cutoff',
                                   'fold_change_cutoff': 'fold_change_cutoff',
                                   'workspace_name': 'workspace_name'}
        with self.assertRaisesRegexp(ValueError,
                                     '"diff_expression_ref" parameter is required, but missing'):
            self.getImpl().upload_featureset_from_diff_expr(self.getContext(),
                                                            invalidate_input_params)

        invalidate_input_params = {'diff_expression_ref': 'diff_expression_ref',
                                   'missing_p_cutoff': 'p_cutoff',
                                   'q_cutoff': 'q_cutoff',
                                   'fold_change_cutoff': 'fold_change_cutoff',
                                   'workspace_name': 'workspace_name'}
        with self.assertRaisesRegexp(ValueError, '"p_cutoff" parameter is required, but missing'):
            self.getImpl().upload_featureset_from_diff_expr(self.getContext(),
                                                            invalidate_input_params)

        invalidate_input_params = {'diff_expression_ref': 'diff_expression_ref',
                                   'p_cutoff': 'p_cutoff',
                                   'missing_q_cutoff': 'q_cutoff',
                                   'fold_change_cutoff': 'fold_change_cutoff',
                                   'workspace_name': 'workspace_name'}
        with self.assertRaisesRegexp(ValueError, '"q_cutoff" parameter is required, but missing'):
            self.getImpl().upload_featureset_from_diff_expr(self.getContext(),
                                                            invalidate_input_params)

        invalidate_input_params = {'diff_expression_ref': 'diff_expression_ref',
                                   'p_cutoff': 'p_cutoff',
                                   'q_cutoff': 'q_cutoff',
                                   'missing_fold_change_cutoff': 'fold_change_cutoff',
                                   'workspace_name': 'workspace_name'}
        with self.assertRaisesRegexp(ValueError,
                                     '"fold_change_cutoff" parameter is required, but missing'):
            self.getImpl().upload_featureset_from_diff_expr(self.getContext(),
                                                            invalidate_input_params)

        invalidate_input_params = {'diff_expression_ref': 'diff_expression_ref',
                                   'p_cutoff': 'p_cutoff',
                                   'q_cutoff': 'q_cutoff',
                                   'fold_change_cutoff': 'fold_change_cutoff',
                                   'missing_workspace_name': 'workspace_name'}
        with self.assertRaisesRegexp(ValueError,
                                     '"workspace_name" parameter is required, but missing'):
            self.getImpl().upload_featureset_from_diff_expr(self.getContext(),
                                                            invalidate_input_params)


    def test_upload_featureset_from_diff_expr(self):

        feature_set_name = 'MyFeatureSet'
        input_params = {
            'diff_expression_ref': self.diff_expression_set_ref,
            'expression_matrix_ref': self.expression_matrix_ref,
            'feature_set_name': feature_set_name,
            'p_cutoff': 0.05,
            'q_cutoff': 0.05,
            'fold_change_cutoff': 1,
            'fold_scale_type': "logarithm",    # optional, if given this is the required value
            'filtered_expression_matrix_suffix': '_filtered_expression_matrix',
            'feature_set_suffix': '_feature_set',
            'workspace_name': self.getWsName(),
            'run_all_combinations': True
        }

        result = self.getImpl().upload_featureset_from_diff_expr(self.getContext(),
                                                                 input_params)[0]

        self.assertTrue('result_directory' in result)
        result_files = os.listdir(result['result_directory'])
        print(result_files)
        expect_result_files = ['gene_results.csv']
        self.assertTrue(all(x in result_files for x in expect_result_files))
        self.assertTrue('up_feature_set_ref_list' in result)
        self.assertTrue('down_feature_set_ref_list' in result)
        self.assertTrue('filtered_expression_matrix_ref_list' in result)
        self.assertTrue('report_name' in result)
        self.assertTrue('report_ref' in result)

        # adding in one test here to make sure that that the filtered expression
        # matrices each have a proper link in the provenance back to the differential
        # expression matrix (individual matrix, not set) that was used to create it

        obj = self.wsClient.get_objects([{'ref': self.diff_expression_set_ref}])[0]
        dl = obj.get('data').get('items')
        dms = map((lambda r: r.get('ref')),dl)

        # check each filtered expression matrix in the set:

        for fem in result.get('filtered_expression_matrix_ref_list'):
            prov = self.wsClient.get_object_provenance([{'ref': fem}])[0].get('provenance')[0]
            self.assertTrue(prov.get( 'input_ws_objects'))
            dem_list = prov.get('input_ws_objects')
            self.assertTrue(isinstance(dem_list, list))
            self.assertTrue(len( dem_list ) == 1)    # should be a list of one
            self.assertTrue(dem_list[0] in dms)      # and in the diff. expr. set list
            dem_info = self.wsClient.get_object_info3({"objects":
                                                            [{"ref": dem_list[0] }]}
                                                            )['infos'][0]

            # ensure that this is really a differential expression matrix

            self.assertTrue( dem_info[2].startswith('KBaseFeatureValues.DifferentialExpressionMatrix'))


    def test_upload_featureset_from_diff_expr_partial_conditions(self):

        feature_set_name = 'MyFeatureSet'
        input_params = {
            'diff_expression_ref': self.diff_expression_set_ref,
            'expression_matrix_ref': self.expression_matrix_ref,
            'feature_set_name': feature_set_name,
            'p_cutoff': 0.05,
            'q_cutoff': 0.05,
            'fold_change_cutoff': 1,
            'filtered_expression_matrix_suffix': '_filtered_expression_matrix',
            'feature_set_suffix': '_feature_set',
            'workspace_name': self.getWsName(),
            'condition_pairs': [{'label_string': ['test_condition_1, test_condition_2']}]
        }

        result = self.getImpl().upload_featureset_from_diff_expr(self.getContext(),
                                                                 input_params)[0]

        self.assertTrue('result_directory' in result)
        result_files = os.listdir(result['result_directory'])
        print(result_files)
        expect_result_files = ['gene_results.csv']
        self.assertTrue(all(x in result_files for x in expect_result_files))
        self.assertTrue('up_feature_set_ref_list' in result)
        self.assertTrue('down_feature_set_ref_list' in result)
        self.assertTrue('filtered_expression_matrix_ref_list' in result)
        self.assertTrue('report_name' in result)
        self.assertTrue('report_ref' in result)



    def test_upload_featureset_from_diff_expr_linear(self):

        feature_set_name = 'MyFeatureSet'
        input_params = {
            'diff_expression_ref': self.diff_expression_set_ref_linear,
            'expression_matrix_ref': self.expression_matrix_ref,
            'feature_set_name': feature_set_name,
            'p_cutoff': 0.05,
            'q_cutoff': 0.05,
            'fold_change_cutoff': 1,
            'filtered_expression_matrix_suffix': '_filtered_expression_matrix',
            'feature_set_suffix': '_feature_set',
            'workspace_name': self.getWsName(),
            'run_all_combinations': True
        }

        result = self.getImpl().upload_featureset_from_diff_expr(self.getContext(),
                                                                 input_params)[0]

        self.assertTrue('result_directory' in result)
        result_files = os.listdir(result['result_directory'])
        print(result_files)
        expect_result_files = ['gene_results.csv']
        self.assertTrue(all(x in result_files for x in expect_result_files))
        self.assertTrue('up_feature_set_ref_list' in result)
        self.assertTrue('down_feature_set_ref_list' in result)
        self.assertTrue('filtered_expression_matrix_ref_list' in result)
        self.assertTrue('report_name' in result)
        self.assertTrue('report_ref' in result)

    def test_to_tsv(self):
        res = self.getImpl().featureset_to_tsv_file(self.getContext(), {
                'featureset_name': self.featureset_name,
                'workspace_name': self.wsName,
            })[0]
        expected = open('data/test_featureset.tsv').read().replace("<genome_ref>", self.genome_ref)
        self.assertEqual(open(res['file_path']).read(), expected)
        pprint(res)
        # test bad input
        with self.assertRaises(ValueError):
            self.getImpl().featureset_to_tsv_file(self.getContext(), {
                'input_ref': self.wsName + '/' + self.featureset_name
            })

    def test_export_tsv(self):
        res = self.getImpl().export_featureset_as_tsv_file(self.getContext(), {
                'input_ref': self.wsName + '/' + self.featureset_name
            })
        pprint(res)
        # test bad input
        with self.assertRaises(ValueError):
            self.getImpl().export_featureset_as_tsv_file(self.getContext(), {
                'featureset_name': self.featureset_name,
                'workspace_name': self.wsName,
            })
