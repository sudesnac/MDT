import os
import numpy as np
import shutil
from mdt.IO import Nifti
from mdt.utils import ModelChunksProcessingStrategy, create_roi, restore_volumes

__author__ = 'Robbert Harms'
__date__ = "2015-11-29"
__maintainer__ = "Robbert Harms"
__email__ = "robbert.harms@maastrichtuniversity.nl"


meta_info = {'title': 'Fit in chunks of voxel ranges',
             'description': 'Processes a model in chunks defined by ranges of voxels.'}


class VoxelRange(ModelChunksProcessingStrategy):

    def __init__(self, nmr_voxels=40000):
        """Optimize a given dataset slice by slice.

        Args:
            nmr_voxels (int): the number of voxels per chunk

        Attributes:
            nmr_voxels (int): the number of voxels per chunk
        """
        super(VoxelRange, self).__init__()
        self.nmr_voxels = nmr_voxels

    def run(self, model, problem_data, output_path, recalculate, worker):
        mask = problem_data.mask
        indices = np.arange(0, np.count_nonzero(mask))
        chunks_dir = os.path.join(output_path, 'chunks')

        self._prepare_chunk_dir(chunks_dir, recalculate)

        for ind_start, ind_end in self._chunks_generator(mask):
            chunk_indices = indices[ind_start:ind_end]

            mask_list = create_roi(mask, mask)
            mask_list[:] = 0
            mask_list[ind_start:ind_end] = 1
            chunk_mask = restore_volumes(mask_list, mask, with_volume_dim=False)

            if len(chunk_indices):
                with self._selected_indices(model, chunk_indices):
                    self._run_on_slice(model, problem_data, chunks_dir, recalculate, worker,
                                       ind_start, ind_end, chunk_mask)

        self._logger.info('Computed all slices, now merging the results')
        return_data = worker.combine(output_path, chunks_dir)
        shutil.rmtree(chunks_dir)
        return return_data

    def _chunks_generator(self, mask):
        """Generate the slices/chunks we will use for the fitting.

        Args:
            mask (ndarray): the mask for all the slices

        Returns:
            tuple (int, int, list): the start of the slice index, the end of the slice index and the list with
                the slices to select from the mask.
        """
        total_nmr_voxels = np.count_nonzero(mask)

        for ind_start in range(0, total_nmr_voxels, self.nmr_voxels):
            ind_end = min(total_nmr_voxels, ind_start + self.nmr_voxels)
            yield ind_start, ind_end

    def _run_on_slice(self, model, problem_data, slices_dir, recalculate, worker, ind_start, ind_end, tmp_mask):
        slice_dir = os.path.join(slices_dir, '{start}_{end}'.format(start=ind_start, end=ind_end))

        if recalculate and os.path.exists(slice_dir):
            shutil.rmtree(slice_dir)

        if worker.output_exists(model, problem_data, slice_dir):
            self._logger.info('Skipping voxels {} to {}, they are already processed.'.format(ind_start, ind_end))
        else:
            self._logger.info('Computing voxels {0} up to {1} ({2} voxels in total, we are at {3:.2%})'.format(
                ind_start, ind_end, np.count_nonzero(problem_data.mask),
                float(ind_start) / np.count_nonzero(problem_data.mask)))

            worker.process(model, problem_data, tmp_mask, slice_dir)
            Nifti.write_volume_maps({'__mask': tmp_mask}, slice_dir, problem_data.volume_header)