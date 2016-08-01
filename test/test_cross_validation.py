from __future__ import absolute_import

from nose.tools import eq_ 

import mhcflurry
import fancyimpute

from . import data_path

from mhcflurry_cloud import (
    cross_validation_folds,
    train_across_models_and_folds,
    models_grid)

def test_imputation():
    imputer = fancyimpute.MICE(
        n_imputations=2, n_burn_in=1, n_nearest_columns=25)
    train_data = (
        mhcflurry.dataset.Dataset.from_csv(
            data_path("bdata.2009.mhci.public.1.txt"))
        .get_alleles(["HLA-A0201", "HLA-A0202", "HLA-A0301"]))

    folds = cross_validation_folds(
        train_data,
        n_folds=3,
        imputer=imputer,
        drop_similar_peptides=True,
        alleles=["HLA-A0201", "HLA-A0202"],
        n_jobs=2,
        verbose=5,
    )

    eq_(set(x.allele for x in folds), {"HLA-A0201", "HLA-A0202"})
    eq_(len(folds), 6)

    for fold in folds:
        eq_(fold.train.unique_alleles(), set([fold.allele]))
        eq_(fold.imputed_train.unique_alleles(), set([fold.allele]))
        eq_(fold.test.unique_alleles(), set([fold.allele]))

def test_cross_validation_no_imputation():
    train_data = (
        mhcflurry.dataset.Dataset.from_csv(
            data_path("bdata.2009.mhci.public.1.txt"))
        .get_alleles(["HLA-A0201", "HLA-A0202", "HLA-A0301"]))

    folds = cross_validation_folds(
        train_data,
        n_folds=3,
        imputer=None,
        drop_similar_peptides=True,
        alleles=["HLA-A0201", "HLA-A0202"]
    )

    eq_(set(x.allele for x in folds), {"HLA-A0201", "HLA-A0202"})
    eq_(len(folds), 6)

    for fold in folds:
        eq_(fold.train.unique_alleles(), set([fold.allele]))
        eq_(fold.test.unique_alleles(), set([fold.allele]))

    models = models_grid(
        activation=["tanh", "relu"],
        layer_sizes=[[4]],
        embedding_output_dim=[8],
        n_training_epochs=[3])
    print(models)

    df = train_across_models_and_folds(
        folds,
        models,
        n_jobs=2,
        verbose=50)
    print(df)
    assert df.test_auc.mean() > 0.6


def test_cross_validation_with_imputation():
    imputer = fancyimpute.MICE(
        n_imputations=2, n_burn_in=1, n_nearest_columns=25)
    train_data = (
        mhcflurry.dataset.Dataset.from_csv(
            data_path("bdata.2009.mhci.public.1.txt"))
        .get_alleles(["HLA-A0201", "HLA-A0202", "HLA-A0301"]))

    folds = cross_validation_folds(
        train_data,
        n_folds=3,
        imputer=imputer,
        drop_similar_peptides=True,
        alleles=["HLA-A0201", "HLA-A0202"],
        n_jobs=3,
        verbose=5,
    )

    eq_(set(x.allele for x in folds), {"HLA-A0201", "HLA-A0202"})
    eq_(len(folds), 6)

    for fold in folds:
        eq_(fold.train.unique_alleles(), set([fold.allele]))
        eq_(fold.imputed_train.unique_alleles(), set([fold.allele]))
        eq_(fold.test.unique_alleles(), set([fold.allele]))

    models = models_grid(
        activation=["tanh", "relu"],
        layer_sizes=[[4]],
        embedding_output_dim=[8],
        n_training_epochs=[3])
    print(models)

    df = train_across_models_and_folds(
        folds,
        models,
        n_jobs=3,
        verbose=5)
    print(df)
    assert df.test_auc.mean() > 0.6
