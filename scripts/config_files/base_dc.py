import os, datetime

# model and training parameters, passed to model and Trainer, respectively
network_parameters = {
    # network_type: model class, one of: MoNet, MoNetUnet (see models.py)
    'network_type': 'MoNetUnet',
    # model_parameters: passed to model class initialiser
    'model_parameters': {
        # model architecture: list of lists for Unet, and list for MoNet (simple convs)
        'layer_sizes': [[32,32,32],[32,32,32],[64,64,64],[64,64,64],[128,128,128],[128,128,128],[256,256,256]],
        # activation_fn: activation function, one of: relu, leaky_relu
        'activation_fn': 'leaky_relu',
        # conv_type: convolution to use, one of: SpiralConv, GMMConv.
        'conv_type': 'SpiralConv',
        # dim: coord dim for GMMConv
        'dim': 2,
        # kernel_size: number of gaussian kernels for GMMConv
        'kernel_size': 3, # number of gaussian kernels
        # spiral_len: size of the spiral for SpiralConv.
        # TODO implement dilation / different spiral len per unet block
        'spiral_len': 7,
        # normalisation: choices: None, "instance"
        'norm': None,
    },
    # training_parameters: used by Trainer to set up model training
    'training_parameters': {
        "max_patience": 400,
        "num_epochs": 1000,
        # optimiser: optimiser to use, one of: adam, sgd
        "optimiser": 'sgd',
        # optimiser_parameters: parameters passed to torch optimiser class
        # for sgd with nesterov momentum use: momentum:0.99, nesterov:True
        "optimiser_parameters": {
            "lr": 1e-4,
            "momentum": 0.99,
            "nesterov": True
        },
        # lr_decay: exponent for exponential learning rate decay: lr*(1-epoch/max_epochs)**lr_decay
        # set to 0 to turn lr decay off
        'lr_decay': 0.9,  # default NNUnet param: 0.9
         'max_epochs_lr_decay': 1000,

        # loss_dictionary: losses to be used for model training and parameters for losses
        # possible keys: 
        #   "cross_entropy"
        #   "focal_loss"
        #   "dice"
        #   "distance_regression": predict geodesic distance from lesion mask
        #       if present in this dict, model will have head with 
        #       layer_sizes - 1 (regression head) - 2 (classification head)
        # values: dict with keys: "weight" and loss arguments (alpha/gamma for focal_loss, class_weights for dice)
        'loss_dictionary': {  
           # 'cross_entropy':{'weight':1},
           # 'focal_loss':{'weight':1, 'alpha':0.4, 'gamma':4},
           # 'dice':{'weight': 1, 'class_weights': [0, 1.]},
           #'distance_regression': {'weight': 1, 'weigh_by_gt': False},
           #'lesion_classification': {'weight': 1},
           #'mae_loss':{'weight':1},
        },
         # metrics: list of metrics that should be printed during training
         # possible values: dice_lesion, dice_nonlesion, precision, recall, tp, fp, fn, tn
        'metrics': ['dice_lesion', 'dice_nonlesion', 'precision', 'recall', 'tp', 'fp', 'fn'], 
        "batch_size": 8,
        "shuffle_each_epoch": True,
        # deep_supervision: add loss at specified levels of the unet (for MoNetUnet).
        # Set to list of levels (eg [6,5,4]), for which to add output layers for additional supervision.
        # 7 is highest level. (standard output).  # TODO add some error checking here, max val should be < 7.
        'deep_supervision': {
              'levels': [6,5,4,3], 
            'weight': [0.5,0.25,0.125,0.0625],
        },
        # ovesampling: oversample lesional vertices to 33% lesional and 66% random.
        # size of epoch will be num_lesional_examples * 3
        'oversampling': True,
        # init_weights: path to checkpoint file to init weights from. Relative to EXPERIMENT_PATH
     'init_weights': None,
    },
    # name: experiment name. If none, experiment is not saved
    'name': None,
}

# data parameters, passed to GraphDataset and Preprocess
data_parameters = {
    
    'hdf5_file_root': "{site_code}_{group}_featurematrix_combat_6.hdf5",
    'site_codes': [
       "H1",
        "H2",
        "H3",
        "H4",
        "H5",
        "H6",
        "H7",
        "H9",
        "H10",
        "H11",
        "H12",
        "H14",
        "H15",
        "H16",
        "H17",
        "H18",
        "H19",
        "H21",
        "H23",
        "H24",
        "H26",
    ],
    'scanners': ['15T','3T'],
    'dataset': 'MELD_dataset_V6.csv',
    #THIS NEEDS TO BE CHANGED IF REAL TRAINING TO BOTH
    'group': 'control',
    "features_to_exclude": [],
    "subject_features_to_exclude": [],
    # features: manually specify features (instead of features_to_exclude)
    "features": [#'.on_lh.lesion.mgh',
        #    '.on_lh.curv.mgh',
        #    '.on_lh.gm_FLAIR_0.25.mgh',
        #    '.on_lh.gm_FLAIR_0.5.mgh',
        #    '.on_lh.gm_FLAIR_0.75.mgh',
        #    '.on_lh.gm_FLAIR_0.mgh',
        #    '.on_lh.pial.K_filtered.sm20.mgh',
        #    '.on_lh.sulc.mgh',
        #    '.on_lh.thickness.mgh',
        #    '.on_lh.w-g.pct.mgh',
        #    '.on_lh.wm_FLAIR_0.5.mgh',
        #    '.on_lh.wm_FLAIR_1.mgh',
        '.combat.on_lh.pial.K_filtered.sm20.mgh',
        '.combat.on_lh.thickness.sm10.mgh',
        '.combat.on_lh.w-g.pct.sm10.mgh',
        '.combat.on_lh.sulc.sm5.mgh',
        '.combat.on_lh.curv.sm5.mgh',
        '.combat.on_lh.gm_FLAIR_0.75.sm10.mgh',
        '.combat.on_lh.gm_FLAIR_0.5.sm10.mgh',
        '.combat.on_lh.gm_FLAIR_0.25.sm10.mgh',
        '.combat.on_lh.gm_FLAIR_0.sm10.mgh',
        '.combat.on_lh.wm_FLAIR_0.5.sm10.mgh',
        '.combat.on_lh.wm_FLAIR_1.sm10.mgh',
        '.inter_z.intra_z.combat.on_lh.pial.K_filtered.sm20.mgh',
        '.inter_z.intra_z.combat.on_lh.thickness.sm10.mgh',
        '.inter_z.intra_z.combat.on_lh.w-g.pct.sm10.mgh',
        '.inter_z.intra_z.combat.on_lh.sulc.sm5.mgh',
        '.inter_z.intra_z.combat.on_lh.curv.sm5.mgh',
        '.inter_z.intra_z.combat.on_lh.gm_FLAIR_0.75.sm10.mgh',
        '.inter_z.intra_z.combat.on_lh.gm_FLAIR_0.5.sm10.mgh',
        '.inter_z.intra_z.combat.on_lh.gm_FLAIR_0.25.sm10.mgh',
        '.inter_z.intra_z.combat.on_lh.gm_FLAIR_0.sm10.mgh',
        '.inter_z.intra_z.combat.on_lh.wm_FLAIR_0.5.sm10.mgh',
        '.inter_z.intra_z.combat.on_lh.wm_FLAIR_1.sm10.mgh',
        '.inter_z.asym.intra_z.combat.on_lh.pial.K_filtered.sm20.mgh',
        '.inter_z.asym.intra_z.combat.on_lh.thickness.sm10.mgh',
        '.inter_z.asym.intra_z.combat.on_lh.w-g.pct.sm10.mgh',
        '.inter_z.asym.intra_z.combat.on_lh.sulc.sm5.mgh',
        '.inter_z.asym.intra_z.combat.on_lh.curv.sm5.mgh',
        '.inter_z.asym.intra_z.combat.on_lh.gm_FLAIR_0.75.sm10.mgh',
        '.inter_z.asym.intra_z.combat.on_lh.gm_FLAIR_0.5.sm10.mgh',
        '.inter_z.asym.intra_z.combat.on_lh.gm_FLAIR_0.25.sm10.mgh',
        '.inter_z.asym.intra_z.combat.on_lh.gm_FLAIR_0.sm10.mgh',
        '.inter_z.asym.intra_z.combat.on_lh.wm_FLAIR_0.5.sm10.mgh',
        '.inter_z.asym.intra_z.combat.on_lh.wm_FLAIR_1.sm10.mgh',
    ],
    # specify this if manually specifying features
    "features_to_replace_with_0": [], 
    "number_of_folds": 10,
    "fold_n": 0,
    # preprocessing_parameters: params for data_preprocessing
    "preprocessing_parameters": {
        "scaling": None, #"scaling_params_GDL.json"
        # zscore: normalise all values by overall mu std. ignores 0s.
        "zscore":'../data/feature_means.json', #False or file_path
    },
    # icosphere_parameters: passed to Icospheres class
    "icosphere_parameters": {
        # distance_type: coords to return as edge attributes (for GMMConv), one of: exact, pseudo
        "distance_type": "exact",
    },
    # augment_data: parameters passed to Augment class
    # dictionary containing augmentation method as keys, and Transform params as values ("p" and "file")
    # possible augmentation methods: spinning, warping, flipping
    # gaussian noise, blurring
    # brightness, contrast
    # low res - I don't think this is implemented
    # gamma - intensity shifting
    "augment_data": {
        'spinning': {'p': 0.2, 'file': 'data/spinning/spinning_ico7_10.npy'},
        'warping': {'p': 0.2, 'file': 'data/warping/warping_ico7_10.npy'},
        'noise': {'p': 0.15},
        'blur': {'p': 0.2},
        'brightness': {'p': 0.15},
        'contrast': {'p': 0.15},
        'low_res': {'p': 0.25},
        'gamma': {'p': 0.15},
        'flipping': {'p': 0.5, 'file': 'data/flipping/flipping_ico7_3.npy'},
                'extend_lesion':{'p': 0.2},
        },
    # combine_hemis: how to combine hemisphere data, one of: None, stack
    # None: no combination of hemispheres. 
    # "stack": stack features of both hemispheres.
    "combine_hemis": None,
    # WARNING: parameters below change the lesion prediction task
    # lobes: if True, train on predicting frontal lobe vs other instead of the lesion predicting task
    "lobes": False,
    # lesion_bias: add this value to lesion values to make prediction task easier
    "lesion_bias": 0,
    # synthetic lesions on synthetic data or on controls.
    'synthetic_data': {
        # run_synthetic: master switch for whether to run the synthetic task. True means run it.
        'run_synthetic':False,
        # n_subs: controls the number of subjects. Randomly sampled from subject ids (i.e. duplicates will exist)
        'n_subs': 1000,
        # use_controls: superimpose lesions on controls, or on white noise features
        'use_controls':True,
        # radius: mean radii of lesions, in units of XX. 
        # For each lesion, actual radius is sampled from N(radius,radius/2)
        'radius': 2,  # realisic: 0.5
        # n_subtypes: number of lesion "fingerprints" generated (number of histological subtypes)
        # A fingerprint determines which features (using proportion_features_abnormal) change, 
        # in which direction they change, and by how much (sampled from U(0,1)*bias).
        'n_subtypes':25,
        # jitter_factor: determines the amount of variance of subjects around the fingerprint bias terms.
        # For each subject with fingerprint f, the actual lesion values are sampled from: N(f, f/jitter_factor)
        'jitter_factor':2,
        # bias: multiplier for fingerprint, determines overall abnormality of lesion.
        # For each subject, on bias term is sampled from N(bias, bias/jitter_factor).
        'bias': 1,
        # proportion_features_abnormal: proportion of the features that are abnormal. 
        # 0.2 means only 20% of features, all others remain unchanged.
        'proportion_features_abnormal': 0.2,  # realistic 0.2
        # proportion_hemispheres_lesional: proportion subjects lesional
        # controls a random variable that determines whether a lesion is added to the control data
        # In the training this could mean two hemispheres from the same subject both have lesions.
        'proportion_hemispheres_lesional': 0.9,  # realistic 0.3
        # smooth_lesion: True / False, if True, returns smoothed lesion features 
        # for better transitions between non-lesion and lesional data
        'smooth_lesion': False,
    }
}