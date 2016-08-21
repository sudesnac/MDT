import glob
import logging
import os
import shutil
import numpy as np
import six
from six import string_types
from mdt import protocols
from mdt.components_loader import BatchProfilesLoader, get_model
from mdt.data_loaders.protocol import ProtocolLoader
from mdt.masking import create_write_median_otsu_brain_mask
from mdt.models.cascade import DMRICascadeModelInterface
from mdt.protocols import load_protocol
from mdt.utils import split_image_path, AutoDict, load_problem_data
import nibabel as nib

__author__ = 'Robbert Harms'
__date__ = "2015-08-21"
__maintainer__ = "Robbert Harms"
__email__ = "robbert.harms@maastrichtuniversity.nl"


class BatchProfile(object):

    def __init__(self):
        """Instantiate this BatchProfile
        """
        self._root_dir = ''

    def set_root_dir(self, root_dir):
        """Set the root dir. That is, the directory we search in for batch fit subjects.

        Args:
            root_dir (str): the root dir to use
        """
        self._root_dir = root_dir

    def get_root_dir(self):
        """Get the root dir this profile uses.

        Returns:
            str: the root dir this batch profile uses.
        """
        return self._root_dir

    def get_models_to_fit(self):
        """Get the list of models we want to fit to every found subject.

        The models can either be real model objects, or strings with the model names.

        Returns:
            list: the list of models we want to fit to the subjects
        """

    def get_subjects(self):
        """Get the information about all the subjects in the current folder.

        Returns:
            list of SubjectInfo: the information about the found subjects
        """

    def profile_suitable(self):
        """Check if this directory can be used to load subjects from using this batch fitting profile.

        This is used for auto detecting the best batch fitting profile to use for loading
        subjects from the given root dir.

        Returns:
            boolean: true if this batch fitting profile can load datasets from this root directory, false otherwise.
        """

    def get_subjects_count(self):
        """Get the number of subjects this batch fitting profile can load from the current root directory.

        Returns:
            int: the number of subjects this batch fitting profile can load from the given directory.
        """


class SimpleBatchProfile(BatchProfile):

    def __init__(self):
        """A base class for quickly implementing a batch profile.

        Implementing classes need only implement the method _get_subjects(). This class will handle the rest.

        Attributes:
            output_base_dir (str): the standard subject output dir, defaults to 'output'
            output_sub_dir (str): if given, a sub directory (in the default output dir) to place the output in
            models_to_fit (list): list of model names or model objects to use during fitting
        """
        super(SimpleBatchProfile, self).__init__()
        self._subjects_found = None
        self._output_base_dir = 'output'
        self._output_sub_dir = None
        self._append_mask_name_to_output_sub_dir = True
        self.models_to_fit = ('BallStick (Cascade)',
                              'Tensor (Cascade)',
                              'Noddi (Cascade)',
                              'BallStickStickStick (Cascade)',
                              'Charmed_r1 (Cascade)',
                              'Charmed_r2 (Cascade)',
                              'Charmed (Cascade)')

    @property
    def output_base_dir(self):
        return self._output_base_dir

    @output_base_dir.setter
    def output_base_dir(self, output_base_dir):
        self._output_base_dir = output_base_dir
        self._subjects_found = None

    @property
    def append_mask_name_to_output_sub_dir(self):
        return self._append_mask_name_to_output_sub_dir

    @append_mask_name_to_output_sub_dir.setter
    def append_mask_name_to_output_sub_dir(self, append_mask_name_to_output_sub_dir):
        self._append_mask_name_to_output_sub_dir = append_mask_name_to_output_sub_dir

    @property
    def output_sub_dir(self):
        return self._output_sub_dir

    @output_sub_dir.setter
    def output_sub_dir(self, output_sub_dir):
        self._output_sub_dir = output_sub_dir
        self._subjects_found = None

    def get_models_to_fit(self):
        return self.models_to_fit

    def get_subjects(self):
        if not self._subjects_found:
            self._subjects_found = self._get_subjects()

        return self._subjects_found

    def profile_suitable(self):
        if not self._subjects_found:
            self._subjects_found = self._get_subjects()

        return len(self._subjects_found) > 0

    def get_subjects_count(self):
        if not self._subjects_found:
            self._subjects_found = self._get_subjects()

        return len(self._subjects_found)

    def _autoload_noise_std(self, subject_id, file_path=None):
        """Try to autoload the noise standard deviation from a noise_std file.

        Args:
            subject_id (str): the subject for which to load the noise std.
            file_path (str): optionally provide the exact file to load.

        Returns:
            float or None: a float if a float could be loaded from a file noise_std, else nothing.
        """
        file_path = file_path or os.path.join(self._root_dir, subject_id, 'noise_std')
        noise_std_files = glob.glob(file_path + '.*')
        if len(noise_std_files):
            return noise_std_files[0]
        return None

    def _get_subjects(self):
        """Get the matching subjects from the given root dir.

        This is the only function that should be implemented by implementing classes to get up and running.

        Returns:
            list of SubjectInfo: the information about the found subjects
        """
        return []

    def _get_subject_output_dir(self, subject_id, mask_fname, subject_base_dir=None):
        """Helper function for generating the output directory for a subject.

        Args:
            subject_id (str): the id of the subject to use
            mask_fname (str): the name of the mask we are using for this subject
            subject_base_dir (str): the base directory for this subject, defaults to
                self._root_dir / subject_id / self.output_base_dir

        Returns:
            str: the path for the output directory
        """
        output_dir = subject_base_dir or os.path.join(self._root_dir, subject_id, self.output_base_dir)

        if self.output_sub_dir:
            output_dir = os.path.join(output_dir, self.output_sub_dir)

        if self._append_mask_name_to_output_sub_dir and mask_fname:
            output_dir = os.path.join(output_dir, split_image_path(mask_fname)[1])

        return output_dir


class SubjectInfo(object):

    @property
    def subject_id(self):
        """Get the ID of this subject.

        Returns:
            str: the id of this subject
        """
        return ''

    @property
    def output_dir(self):
        """Get the output folder for this subject.

        Returns:
            str: the output folder
        """
        return ''

    def get_problem_data(self, dtype=np.float32):
        """Get the DMRIProblemData for this subject.

        This is the data we will use during model fitting.

        Args:
            dtype (numpy dtype): the datatype we will use for the problem data

        Returns:
            DMRIProblemData: the problem data to use during model fitting
        """

    def get_mask_filename(self):
        """Get the filename of the mask to load.

        Returns:
            str: the filename of the mask to load
        """


class SimpleSubjectInfo(SubjectInfo):

    def __init__(self, subject_id, dwi_fname, protocol_loader, mask_fname, output_dir, gradient_deviations=None,
                 noise_std=None):
        """This class contains all the information about found subjects during batch fitting.

        It is returned by the method get_subjects() from the class BatchProfile.

        Args:
            subject_id (str): the subject id
            dwi_fname (str): the filename with path to the dwi image
            protocol_loader (ProtocolLoader): the protocol loader that can load us the protocol
            mask_fname (str): the filename of the mask to load. If None a mask is auto generated.
            output_dir (str): the output directory
            gradient_deviations (str) if given, the path to the gradient deviations
            noise_std (float, ndarray, str): either None for automatic noise detection or a float with the noise STD
                to use during fitting or an ndarray with one value per voxel.
        """
        self._subject_id = subject_id
        self._dwi_fname = dwi_fname
        self._protocol_loader = protocol_loader
        self._mask_fname = mask_fname
        self._output_dir = output_dir
        self._gradient_deviations = gradient_deviations
        self._noise_std = noise_std

        if self._mask_fname is None:
            self._mask_fname = os.path.join(self.output_dir, 'auto_generated_mask.nii.gz')

    @property
    def subject_id(self):
        return self._subject_id

    @property
    def output_dir(self):
        return self._output_dir

    def get_problem_data(self, dtype=np.float32):
        protocol = self._protocol_loader.get_protocol()
        brain_mask_fname = self.get_mask_filename()
        return load_problem_data(self._dwi_fname, protocol, brain_mask_fname,
                                 gradient_deviations=self._get_gradient_deviations(), noise_std=self._noise_std)

    def get_subject_id(self):
        return self.subject_id

    def get_mask_filename(self):
        if not os.path.isfile(self._mask_fname):
            logger = logging.getLogger(__name__)
            logger.info('Creating a brain mask for subject {0}'.format(self.subject_id))

            protocol = self._protocol_loader.get_protocol()
            create_write_median_otsu_brain_mask(self._dwi_fname, protocol, self._mask_fname)

        return self._mask_fname

    def _get_gradient_deviations(self):
        if self._gradient_deviations is not None:
            return nib.load(self._gradient_deviations).get_data()
        return None


class BatchSubjectSelection(object):

    def get_selection(self, subjects):
        """Get the selection of subjects from the given list of subjects.

        Args:
            subjects (list of SubjectInfo): the list of subjects from which we can choose which one to process

        Returns:
            list of SubjectInfo: the given list or a subset of the given list with the subjects to process.
        """
        pass


class AllSubjects(BatchSubjectSelection):
    """Selects all subjects for use in the processing"""

    def get_selection(self, subjects):
        return subjects


class SelectedSubjects(BatchSubjectSelection):

    def __init__(self, subject_ids=None, indices=None, start_from=None):
        """Only process the selected subjects.

        This method allows either a selection by index (unsafe for the order may change) or by subject name/ID (more
        safe in general). If start_from is given it additionally limits the list of selected subjects to include
        only those after that index.

        This essentially creates three different subsets of the given list of subjects and will only process
        those subjects in the intersection of all those sets.

        Set any one of the options to None to ignore them.

        Args:
            subject_ids (list of str): the list of names of subjects to process
            indices (list/tuple of int): the list of indices of subjects we wish to process
            start_from (list or int): the index of the name of the subject from which we want to start processing.
        """
        self.subject_ids = subject_ids
        self.indices = indices
        self.start_from = start_from

    def get_selection(self, subjects):
        starting_pos = self._get_starting_pos(subjects)

        if self.indices is None and self.subject_ids is None:
            return subjects[starting_pos:]

        if self.indices:
            subjects = [subject for ind, subject in enumerate(subjects) if ind in self.indices and ind >= starting_pos]

        if self.subject_ids:
            subjects = list(filter(lambda subject: subject.subject_id in self.subject_ids, subjects))

        return subjects

    def _get_starting_pos(self, subjects):
        if self.start_from is None:
            return 0

        if isinstance(self.start_from, six.string_types):
            for ind, subject in enumerate(subjects):
                if subject.subject_id == self.start_from:
                    return ind

        for ind, subject in enumerate(subjects):
            if ind == int(self.start_from):
                return ind


class BatchFitProtocolLoader(ProtocolLoader):

    def __init__(self, base_dir, protocol_fname=None, protocol_options=None, bvec_fname=None, bval_fname=None):
        """A simple protocol loader for loading a protocol from a protocol file or bvec/bval files.

        This either loads the protocol file if present, or autoloads the protocol using the auto_load_protocol
        from the protocol module.
        """
        super(BatchFitProtocolLoader, self).__init__()
        self._base_dir = base_dir
        self._protocol_fname = protocol_fname
        self._bvec_fname = bvec_fname
        self._bval_fname = bval_fname
        self._protocol_options= protocol_options

    def get_protocol(self):
        super(BatchFitProtocolLoader, self).get_protocol()

        if self._protocol_fname and os.path.isfile(self._protocol_fname):
            return load_protocol(self._protocol_fname)

        return protocols.auto_load_protocol(self._base_dir, protocol_options=self._protocol_options,
                                            bvec_fname=self._bvec_fname, bval_fname=self._bval_fname)


class BatchFitSubjectOutputInfo(object):

    def __init__(self, subject_info, output_path, model_name):
        """This class is used in conjunction with the function run_function_on_batch_fit_output().

        Args:
            subject_info (SubjectInfo): the information about the subject before batch fitting
            output_path (str): the full path to the directory with the maps
            model_name (str): the name of the model (not a path)
        """
        self.subject_info = subject_info
        self.output_path = output_path
        self.model_name = model_name

    @property
    def mask_name(self):
        return split_image_path(self.subject_info.get_mask_filename())[1]

    @property
    def subject_id(self):
        return self.subject_info.subject_id


class BatchFitOutputInfo(object):

    def __init__(self, data_folder, batch_profile=None, subjects_selection=None):
        """Single point of information about batch fitting output.

        Args:
            data_folder (str): The data folder with the output files
            batch_profile (BatchProfile class or str): the batch profile to use, can also be the name
                of a batch profile to load. If not given it is auto detected.
            subjects_selection (BatchSubjectSelection): the subjects to use for processing.
                If None all subjects are processed.
        """
        self._data_folder = data_folder
        self._batch_profile = batch_profile_factory(batch_profile, data_folder)
        self._subjects_selection = subjects_selection or AllSubjects()
        self._subjects = self._subjects_selection.get_selection(self._batch_profile.get_subjects())
        self._mask_paths = {}

    def subject_output_info_generator(self):
        """Generates for every subject an output info object which contains all relevant information about the subject.

        Returns:
            generator: returns an BatchFitSubjectOutputInfo per subject
        """
        model_names = self._get_single_model_names(self._batch_profile.get_models_to_fit())

        for subject_info in self._subjects:
            for model_name in model_names:
                output_path = os.path.join(subject_info.output_dir, model_name)
                if os.path.isdir(output_path):
                    yield BatchFitSubjectOutputInfo(subject_info, output_path, model_name)

    @staticmethod
    def _get_single_model_names(model_names):
        """Resolve the single model names from the list of (possibly cascade) model names from the BatchProfile"""
        lookup_cache = {}

        def get_names(current_names):
            single_model_names = []

            for model_name in current_names:
                if model_name not in lookup_cache:
                    model = get_model(model_name)
                    if isinstance(model, DMRICascadeModelInterface):
                        resolved_names = get_names(model.get_model_names())
                        lookup_cache[model_name] = resolved_names
                    else:
                        lookup_cache[model_name] = [model_name]

                single_model_names.extend(lookup_cache[model_name])

            return single_model_names

        return list(set(get_names(model_names)))


def run_function_on_batch_fit_output(data_folder, func, batch_profile=None, subjects_selection=None):
    """Run a function on the output of a batch fitting routine.

    This enables you to run a function on every model output from every subject. The callback python function
    should accept as single argument an instance of the class BatchFitSubjectOutputInfo.

    Args:
        data_folder (str): The data folder with the output files
        func (python function): the python function we should call for every map and model.
            This should accept as single parameter a BatchFitSubjectOutputInfo.
        batch_profile (BatchProfile class or str): the batch profile to use, can also be the name
            of a batch profile to load. If not given it is auto detected.
        subjects_selection (BatchSubjectSelection): the subjects to use for processing.
            If None all subjects are processed.

    Returns:
        dict: indexed by subject->model_name, values are the return values of the users function
    """
    output_info = BatchFitOutputInfo(data_folder, batch_profile, subjects_selection=subjects_selection)

    results = AutoDict()
    for subject in output_info.subject_output_info_generator():
        results[subject.subject_id][subject.model_name] = func(subject)

    return results.to_normal_dict()


def batch_profile_factory(batch_profile, data_folder):
    """Wrapper function for getting a batch profile.

    Args:
        batch_profile (None, string or BatchProfile): indication of the batch profile to load.
            If a string is given it is loaded from the users home folder. Else the best matching profile is returned.
        data_folder (str): the data folder we want to use the batch profile on.

    Returns:
        If the given batch profile is None we return the output from get_best_batch_profile(). If batch profile is
        a string we load it from the batch profiles loader. Else we return the input.
    """
    if batch_profile is None:
        batch_profile = get_best_batch_profile(data_folder)
    elif isinstance(batch_profile, string_types):
        batch_profile = BatchProfilesLoader().load(batch_profile)

    batch_profile.set_root_dir(data_folder)
    return batch_profile


def get_best_batch_profile(data_folder):
    """Get the batch profile that best matches the given directory.

    Args:
        data_folder (str): the directory for which to get the best batch profile.

    Returns:
        BatchProfile: the best matching batch profile.
    """
    profile_loader = BatchProfilesLoader()
    crawlers = [profile_loader.load(c) for c in profile_loader.list_all()]

    best_crawler = None
    best_subjects_count = 0
    for crawler in crawlers:
        crawler.set_root_dir(data_folder)
        if crawler.profile_suitable():
            tmp_count = crawler.get_subjects_count()
            if tmp_count > best_subjects_count:
                best_crawler = crawler
                best_subjects_count = tmp_count

    return best_crawler


def collect_batch_fit_output(data_folder, output_dir, batch_profile=None, subjects_selection=None, symlink=True,
                             move=False):
    """Load from the given data folder all the output files and put them into the output directory.

    If there is more than one mask file available the user has to choose which mask to use using the mask_name
    keyword argument. If it is not given an error is raised.

    The results for the chosen mask it placed in the output folder per subject. Example:
        <output_dir>/<subject_id>/<model_name>

    Args:
        data_folder (str): The data folder with the output files
        output_dir (str): The path to the output folder where all the files will be put.
        batch_profile (BatchProfile class or str): the batch profile to use, can also be the name
            of a batch profile to load. If not given it is auto detected.
        subjects_selection (BatchSubjectSelection): the subjects to use for processing.
            If None all subjects are processed.
        symlink (boolean): only available under Unix OS's. Creates a symlink instead of copying.
        move (boolean): instead of copying the files, move them to a new position. If set, this overrules the parameter
            symlink.
    """
    def copy_function(subject_info):
        if not os.path.exists(os.path.join(output_dir, subject_info.subject_id)):
            os.makedirs(os.path.join(output_dir, subject_info.subject_id))

        subject_out = os.path.join(output_dir, subject_info.subject_id, subject_info.model_name)

        if os.path.exists(subject_out) or os.path.islink(subject_out):
            if os.path.islink(subject_out):
                os.unlink(subject_out)
            else:
                shutil.rmtree(subject_out)

        if move:
            shutil.move(subject_info.output_path, subject_out)
        else:
            if symlink:
                os.symlink(subject_info.output_path, subject_out)
            else:
                shutil.copytree(subject_info.output_path, subject_out)

    run_function_on_batch_fit_output(data_folder, copy_function, batch_profile=batch_profile,
                                     subjects_selection=subjects_selection)
