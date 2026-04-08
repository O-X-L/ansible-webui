export const API_STATUS_CODES_OK = [200, 304];
export const EXEC_STATUS_FAILED = 3;
export const EXEC_STATUS_SUCCESS = 4;
export const EXEC_STATUS_CANCELED = 6;
export const JOB_EXEC_STATI_ACTIVE = [0, 1, 2, 5, 7];
export const REPO_EXEC_STATI_ACTIVE = [1, 2, 7];
export const HASH_PARAM_SEARCH = 'search';
export const SECRET_PLACEHOLDER = '⬤'.repeat(15);
export const WAIT_MOUNT_SCROLL = 2000;
export const WAIT_MOUNT_MODAL = 2500;


interface repoKindMapType {
    static: number,
    git: number,
}

export const repoKindMap: repoKindMapType = {'static': 1, 'git': 2};

export const REGEX_FORM_INT_GT0 = /^(|[1-9][0-9]{0,5})$/;
