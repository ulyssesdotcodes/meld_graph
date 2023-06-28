### called by evaluate.sh which is launched by cross_val_aucs.py
### Runs one model across a val /test cohort and will either save predictions
### or calculate summary statistics
import argparse
import meld_graph
import meld_graph.models
import meld_graph.experiment
import meld_graph.dataset
import meld_graph.data_preprocessing
import meld_graph.evaluation

from meld_graph.dataset import GraphDataset
from meld_classifier.meld_cohort import MeldCohort

from meld_graph.evaluation import Evaluator
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Script to evaluate one model on either train, test, val, or trainval. Val as default does not save predictions"""
    )
    parser.add_argument("--model_path", help="path to trained model config")
    parser.add_argument("--split", help="train, test, val, or trainval")

    args = parser.parse_args()
    exp = meld_graph.experiment.Experiment.from_folder(args.model_path)
    if args.split == "trainval":
        subjects = exp.data_parameters["train_ids"] + exp.data_parameters["val_ids"]
    else:
        sub_split = args.split + "_ids"
        subjects = exp.data_parameters[sub_split]
    cohort = MeldCohort(
        hdf5_file_root=exp.data_parameters["hdf5_file_root"],
        dataset=exp.data_parameters["dataset"],
    )
    features = exp.data_parameters["features"]
    exp.data_parameters["augment_data"] = {}
    dataset = GraphDataset(subjects, cohort, exp.data_parameters, mode="test")

    eva = Evaluator(
        experiment=exp,
        checkpoint_path=args.model_path,
        save_dir=args.model_path,
        make_images=False,
        dataset=dataset,
        cohort=cohort,
        subject_ids=subjects,
        mode="test",
    )
    # only save predictions on test, no need on vals but instead calculate ROCs
    if args.split == "test":
        save_prediction = True
        roc_curves_thresholds = None
        suffix = ""
    elif args.split == "val":
        save_prediction = False
        roc_curves_thresholds = np.linspace(0, 1, 21)
        suffix = ""
    elif args.split == "train":
        save_prediction = True
        roc_curves_thresholds = None
        suffix = "_train"
    elif args.split == "trainval":
        save_prediction = True
        roc_curves_thresholds = None
        suffix = "_trainval"
    else:
        raise NotImplementedError(args.split)

    eva.load_predict_data(
        save_prediction=save_prediction,
        roc_curves_thresholds=roc_curves_thresholds,
        save_prediction_suffix=suffix,
    )

    # # calculate stats
    eva.stat_subjects()
