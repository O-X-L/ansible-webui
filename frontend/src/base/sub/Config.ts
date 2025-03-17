export const API_STATUS_CODES_OK = [200, 304];

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
