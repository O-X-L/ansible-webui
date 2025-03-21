export const API_STATUS_CODES_OK = [200, 304];
export const JOB_EXEC_STATI_ACTIVE = [0, 1, 2, 7];
export const REPO_EXEC_STATI_ACTIVE = [1, 2, 7];
export const PARAM_JOB = 'job';
export const PARAM_SEARCH = 'search';
export const SECRET_PLACEHOLDER = '⬤'.repeat(15);


interface repoKindMapType {
    static: number,
    git: number,
}

export const repoKindMap: repoKindMapType = {'static': 1, 'git': 2};
