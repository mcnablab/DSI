import numpy as np
import nibabel as nib
import dsiadapt as dsi
import dipy.core.gradients as grad

def loaddata(filename):
    # Load data
    data = nib.load('data/' + filename + '.nii.gz').get_data();

    # Swap data dim such that the visualization is good
    filename_short = filename[6:12]; # Use key letters to differentiate data
    if filename_short == 'exvivo':
	data_swap = np.swapaxes(data, 0, 1);
	data_swap = np.swapaxes(data_swap, 1, 2);
	data_swap = data_swap[::-1,...]
	data_swap = data_swap[:, ::-1,...]
    elif filename_short == 'invivo':
	data_swap = np.swapaxes(data, 1, 2);
	data_swap = data_swap[::-1,...]
    else:
	print('Error: no such option!!');
    return data_swap

def loadgtab(filename):
    # Load bvals and bvecs
    filename_short = filename[0:12]; # Use key letters to differentiate data
    gtab = grad.gradient_table('data/' + filename_short + '_bvals.txt', 'data/' + filename_short + '_bvecs.txt');
    
    # Swap bvecs dim such that the visualization is good
    filename_short = filename[6:12];
    if filename_short == 'exvivo':
	bvecstmp = np.zeros(gtab.bvecs.shape);
	bvecstmp[:, 0] = -gtab.bvecs[:, 1];
	bvecstmp[:, 1] = -gtab.bvecs[:, 2];
	bvecstmp[:, 2] = gtab.bvecs[:, 0]; 
    elif filename_short == 'invivo':
	bvecstmp = np.zeros(gtab.bvecs.shape);
	bvecstmp[:, 0] = -gtab.bvecs[:, 0];
	bvecstmp[:, 1] = gtab.bvecs[:, 2];
	bvecstmp[:, 2] = gtab.bvecs[:, 1]; 
    else:
	print('Error: no such option!!');
    gtab_swap = grad.gradient_table_from_bvals_bvecs(gtab.bvals, bvecstmp)
    return gtab_swap

def loadtime(filename):
    # Load diffusion time and gradient pulse duration time
    filename = filename[6:12]; # Use key letters to differentiate data
    if filename == 'exvivo':
        bigdelta = 29.4 * 10**-3; # Unit: second
	smalldelta = 16.7 * 10**-3;
    elif filename == 'invivo':
	bigdelta = 20.9 * 10**-3;
	smalldelta = 12.9 * 10**-3;
    else:
	print('Error: no such option!!')
    return bigdelta, smalldelta

def weight(pdfslice, order):
    qgridsz = pdfslice.shape[0]
    center = qgridsz//2
    tmp = np.arange(qgridsz) - center
    x, y = np.meshgrid(tmp, tmp)
    r = np.sqrt(x ** 2 + y ** 2)
    weightedpdfslice = pdfslice * r**order
    return weightedpdfslice

def downsample(data, gtab, downratio):
    qtable = dsi.create_qtable(gtab);

    idx1 = (np.mod(np.abs(qtable[:, 0]), downratio)==0) * (np.mod(np.abs(qtable[:, 1]), downratio)==0) * (np.mod(np.abs(qtable[:, 2]), downratio)==0)
    
    idx2 = np.logical_or(np.logical_or(np.abs(qtable[:, 0]) == qtable.max(), np.abs(qtable[:, 1]) == qtable.max()), np.abs(qtable[:, 2]) == qtable.max());
    
    idxremain = np.logical_or(idx1, idx2)  
    idxremove = np.logical_not(idxremain);

    subdata = data
    subdata[..., idxremove] = 0; # Subsample the data by inserting 0

    return subdata

def uniquebvals(data, bvals):
    uniqbvals = np.unique(bvals)
    uniqdata = np.zeros((uniqbvals.shape[0], 1))
    for i in range(uniqbvals.shape[0]):
        idx = bvals == uniqbvals[i]
        tmp = data[idx,...]
        uniqdata[i] = tmp.mean()
    return uniqdata, uniqbvals
    return subdata
