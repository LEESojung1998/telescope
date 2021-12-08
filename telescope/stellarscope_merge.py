# -*- coding: utf-8 -*-
""" Stellarscope merge

"""

from __future__ import print_function
from __future__ import absolute_import
from builtins import super

import os
import logging as lg
import pkgutil
from time import time
import scipy
import pandas as pd

from . import utils

__author__ = 'Matthew L. Bendall'
__copyright__ = "Copyright (C) 2021 Matthew L. Bendall"

class StellarscopeMergeOptions(utils.OptionsBase):
    """

    """
    OPTS = pkgutil.get_data('telescope', 'cmdopts/stellarscope_merge.yaml')

    def __init__(self, args):
        super().__init__(args)


def run(args):
    """

    Args:
        args:

    Returns:

    """
    opts = StellarscopeMergeOptions(args)
    utils.configure_logging(opts)
    lg.debug('\n{}\n'.format(opts))
    total_time = time()

    # import the relevant data files
    lg.info('Loading gene counts.')
    gene_counts = scipy.io.mmread(opts.gene_counts)
    gene_features = pd.read_csv(opts.gene_features, sep = '\t')
    gene_barcodes = pd.read_csv(opts.gene_barcodes, sep = '\t')

    lg.info('Loading transposable element counts.')
    TE_counts = scipy.io.mmread(opts.TE_counts)
    TE_features = pd.read_csv(opts.TE_features, sep='\t')
    TE_barcodes = pd.read_csv(opts.TE_barcodes, sep='\t')

    if len(TE_barcodes) != len(gene_barcodes) or not TE_barcodes.iloc[:,0].isin(gene_barcodes.iloc[:,0]).all():
        lg.warning('Barcode sets do not match, only keeping barcodes present in both sets.')

    # align barcode sets to each other, only keeping barcodes present in both sets
    gene_bc_aligned, TE_bc_aligned = gene_barcodes.align(TE_barcodes, join='inner', axis=0)
    gene_count_rows, TE_count_rows = gene_bc_aligned.index.to_numpy(), TE_bc_aligned.index.to_numpy()

    # use common barcodes to combine count matrices
    lg.info('Combining count matrices.')
    merged_mtx = scipy.sparse.hstack([gene_counts[gene_count_rows,:],
                                        TE_counts[TE_count_rows,:]])
    merged_features = gene_features.append(TE_features)
    merged_barcodes = pd.Series(gene_bc_aligned.values,
                                index = range(len(gene_bc_aligned.values)))


    # save files
    scipy.io.mmwrite(opts.outfile_path('merged_counts.mtx'), merged_mtx)
    merged_features.to_csv(opts.outfile_path('merged_features.tsv'), sep = '\t')
    merged_barcodes.to_csv(opts.outfile_path('merged_barcodes.tsv'), sep = '\t')

    return

