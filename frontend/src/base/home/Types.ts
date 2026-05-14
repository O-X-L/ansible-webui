export interface executionPromptVarType {
    name: string,
    varName: string,
    kind: 'text'|'dropdown',
    required: boolean,
    choices: string[],
    defaultChoice: string|null,
    regex: string,
}

export interface executionPromptsType {
    fields: string[],
    vars: executionPromptVarType[],
}

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
    ssh_hostkey_file: string|null,
}

export interface credentialsSharedType {
    id: number,
    name: string,
    connect_user: string,
    become_user: string,
    vault_file: string,
    vault_id: string,
    vault_pass_is_set: boolean,
    become_pass_is_set: boolean,
    connect_pass_is_set: boolean,
    ssh_key_is_set: boolean,
}
export interface credentialsUserType extends credentialsSharedType {
    category: string,
}

interface statsJobsMapping {
    jobs: any
    users: any
    status: any
    stats: any
    host_stats: any
}
export type statsExecutionHost = [
    string,  // 0 hostname
    number,  // 1 unreachable (0/1 boolean)
    number,  // 2 tasks-skipped
    number,  // 3 tasks-ok
    number,  // 4 tasks-failed
    number,  // 5 tasks-rescued
    number,  // 6 tasks-ignored
    number,  // 7 tasks-changed
]
export type statsExecution = [
    number,  // 0 job id
    number,  // 1 status id
    number|null,  // 2 user id
    number,  // 3 duration
    number,  // 4 time
    number,  // 5 failed (0/1 boolean)
    statsExecutionHost[],  // 6
];
export interface statsJobs {
    stats: statsExecution[]
    mapping: statsJobsMapping
}
