export const API_STATUS_CODES_OK = [200, 304];
export const JOB_EXEC_STATI_ACTIVE = [0, 1, 2, 7];
export const REPO_EXEC_STATI_ACTIVE = [1, 2, 7];

export interface executionPromptVarType {
    name: string,
    varName: string,
    kind: 'text'|'dropdown',
    required: boolean,
    choices: string[],
    regex: string,
}

export interface executionPromptsType {
    enforce: boolean,
    fields: string[],
    vars: executionPromptVarType[],
}

interface repoKindMapType {
    static: number,
    git: number,
}

export const repoKindMap: repoKindMapType = {'static': 1, 'git': 2};
