# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os
import json

from FeatureSetUtils.Utils.FeatureSetBuilder import FeatureSetBuilder
from FeatureSetUtils.Utils.AveExpressionMatrixBuilder import AveExpressionMatrixBuilder
from FeatureSetUtils.Utils.download import FeatureSetDownload
#END_HEADER


class FeatureSetUtils:
    '''
    Module Name:
    FeatureSetUtils

    Module Description:
    A KBase module: FeatureSetUtils
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "1.1.6"
    GIT_URL = "https://github.com/kbaseapps/FeatureSetUtils.git"
    GIT_COMMIT_HASH = "67b986ebb4887730098b36dd2145b7177cbdd1ad"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.config = config
        self.config['SDK_CALLBACK_URL'] = os.environ['SDK_CALLBACK_URL']
        self.config['KB_AUTH_TOKEN'] = os.environ['KB_AUTH_TOKEN']
        self.fsdld = FeatureSetDownload(config)
        #END_CONSTRUCTOR
        pass


    def upload_featureset_from_diff_expr(self, ctx, params):
        """
        upload_featureset_from_diff_expr: create a FeatureSet object from a RNASeqDifferentialExpression object
        :param params: instance of type "UploadFeatureSetFromDiffExprInput"
           (required params: diff_expression_ref:
           DifferetialExpressionMatrixSet object reference
           expression_matrix_ref: ExpressionMatrix object reference p_cutoff:
           p value cutoff q_cutoff: q value cutoff fold_scale_type: one of
           ["linear", "log2+1", "log10+1"]  DEPRICATED NOW
           fold_change_cutoff: fold change cutoff feature_set_suffix: Result
           FeatureSet object name suffix filtered_expression_matrix_suffix:
           Result ExpressionMatrix object name suffix workspace_name: the
           name of the workspace it gets saved to run_all_combinations: run
           all paired condition combinations (default true) or
           condition_labels: conditions for expression set object) ->
           structure: parameter "diff_expression_ref" of type "obj_ref" (An
           X/Y/Z style reference), parameter "expression_matrix_ref" of type
           "obj_ref" (An X/Y/Z style reference), parameter "p_cutoff" of
           Double, parameter "q_cutoff" of Double, parameter
           "fold_scale_type" of String, parameter "fold_change_cutoff" of
           Double, parameter "feature_set_suffix" of String, parameter
           "filtered_expression_matrix_suffix" of String, parameter
           "workspace_name" of String, parameter "run_all_combinations" of
           type "boolean" (A boolean - 0 for false, 1 for true. @range (0,
           1)), parameter "condition_labels" of list of String
        :returns: instance of type "UploadFeatureSetFromDiffExprResult"
           (result_directory: folder path that holds all files generated by
           upload_featureset_from_diff_expr up_feature_set_ref_list: list of
           generated upper FeatureSet object reference
           down_feature_set_ref_list: list of generated down FeatureSet
           object reference filtered_expression_matrix_ref_list: list of
           generated filtered ExpressionMatrix object reference report_name:
           report name generated by KBaseReport report_ref: report reference
           generated by KBaseReport) -> structure: parameter
           "result_directory" of String, parameter "up_feature_set_ref_list"
           of list of type "obj_ref" (An X/Y/Z style reference), parameter
           "down_feature_set_ref_list" of list of type "obj_ref" (An X/Y/Z
           style reference), parameter "filtered_expression_matrix_ref_list"
           of list of type "obj_ref" (An X/Y/Z style reference), parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN upload_featureset_from_diff_expr
        print('--->\nRunning FeatureSetUtils.upload_featureset_from_diff_expr\nparams:')
        print(json.dumps(params, indent=1))

        for key, value in params.iteritems():
            if isinstance(value, str):
                params[key] = value.strip()

        fs_builder = FeatureSetBuilder(self.config)
        returnVal = fs_builder.upload_featureset_from_diff_expr(params)
        #END upload_featureset_from_diff_expr

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method upload_featureset_from_diff_expr return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def calculate_average_expression_matrix(self, ctx, params):
        """
        calculate_average_expression_matrix: create an average ExpressionMatrix object from a ExpressionMatrix object
        :param params: instance of type "CalAveExpressionMatrixInput"
           (required params: expression_matrix_ref: ExpressionMatrix object
           reference output_suffix: output average ExpressionMatrix name
           suffix workspace_name: the name of the workspace it gets saved to)
           -> structure: parameter "expression_matrix_ref" of type "obj_ref"
           (An X/Y/Z style reference), parameter "output_suffix" of String,
           parameter "workspace_name" of String
        :returns: instance of type "CalAveExpressionMatrixResult"
           (average_expression_matrix_ref: generated average ExpressionMatrix
           object reference report_name: report name generated by KBaseReport
           report_ref: report reference generated by KBaseReport) ->
           structure: parameter "average_expression_matrix_ref" of type
           "obj_ref" (An X/Y/Z style reference), parameter "report_name" of
           String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN calculate_average_expression_matrix
        print('--->\nRunning FeatureSetUtils.calculate_average_expression_matrix\nparams:')
        print(json.dumps(params, indent=1))

        for key, value in params.iteritems():
            if isinstance(value, str):
                params[key] = value.strip()

        ave_builder = AveExpressionMatrixBuilder(self.config)
        returnVal = ave_builder.calculate_average_expression_matrix(params)
        #END calculate_average_expression_matrix

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method calculate_average_expression_matrix return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def featureset_to_tsv_file(self, ctx, params):
        """
        :param params: instance of type "FeatureSetToFileParams" ->
           structure: parameter "featureset_name" of String, parameter
           "workspace_name" of String
        :returns: instance of type "FeatureSetTsvFiles" -> structure:
           parameter "file_path" of String
        """
        # ctx is the context object
        # return variables are: files
        #BEGIN featureset_to_tsv_file
        self.fsdld.validate_params(params)
        params['featureset_ref'] = params['workspace_name'] + "/" + params['featureset_name']
        pg_name, files = self.fsdld.to_tsv(params)
        #END featureset_to_tsv_file

        # At some point might do deeper type checking...
        if not isinstance(files, dict):
            raise ValueError('Method featureset_to_tsv_file return value ' +
                             'files is not type dict as required.')
        # return the results
        return [files]

    def export_featureset_as_tsv_file(self, ctx, params):
        """
        :param params: instance of type "ExportParams" -> structure:
           parameter "input_ref" of String
        :returns: instance of type "ExportOutput" -> structure: parameter
           "shock_id" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN export_featureset_as_tsv_file
        print('--->\nRunning FeatureSetUtils.export_featureset_as_tsv_file\nparams:')
        print(json.dumps(params, indent=1))
        self.fsdld.validate_params(params, {'input_ref'})
        params['featureset_ref'] = params['input_ref']
        fs_name, files = self.fsdld.to_tsv(params)
        output = self.fsdld.export(list(files.values()), fs_name, params)
        #END export_featureset_as_tsv_file

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method export_featureset_as_tsv_file return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
