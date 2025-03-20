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

export interface executionType {
    id: number,
    job: number,
    user: number,
    user_name: string,
    result: number,
    status: number,
    status_name: string,
    log_stdout: string|null,
    log_stdout_url: string|null,
    log_stderr: string|null,
    log_stderr_url: string|null,
    comment: string|null,
    credential_global: number|null,
    credential_user: number|null,
    command: string|null,
    log_stdout_repo: string|null,
    log_stderr_repo: string|null,
    log_stdout_repo_url: string|null,
    log_stderr_repo_url: string|null,
    job_name: string,
    job_comment: string,
    time_start: string,
    time_fin: string,
    failed: boolean,
    error_s: string|null,
    error_m: string|null,
    time_duration: string,
}

export interface jobType {
    id: number,
    name: string,
    playbook_file: string,
    inventory_file: string|null,
    repository: number|null,
    schedule: string|null,
    enabled: boolean,
    limit: string|null,
    verbosity: number,
    mode_diff: boolean,
    mode_check: boolean,
    tags: string|null,
    tags_skip: string|null,
    comment: string|null,
    environment_vars: string|null,
    cmd_args: string|null,
    credentials_default: number|null,
    credentials_needed: boolean,
    credentials_category: string|null,
    execution_prompts: string|null,
    execution_prompts_json: string|null,
    next_run: string|null,
    executions: executionType[],
}
