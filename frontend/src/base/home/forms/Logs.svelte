<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { InfoCircleSolid, CloseCircleSolid, StopSolid } from 'flowbite-svelte-icons';
    import { Spinner, Heading, Button, Tooltip, Toggle, Alert } from 'flowbite-svelte';  // Modal

    import Modal from '../../../flowbite-custom/Modal.svelte';

    import { share } from '../../Share.js';
    import { tq } from '../../../util/translate.js';
    // import { type executionType } from '../Types.js';
    import { apiGet, apiEdit } from '../../../util/api.js';
    import { JOB_EXEC_STATI_ACTIVE } from '../../Config.js';
    import APIResponseHandler from '../../snippets/ApiResponseHandler.svelte';
    import { classModalBackdrop, classSpinnerDiv, classCenterChildDiv } from '../../Style.js';

    let {
        open = $bindable(false),
        jobName = '',
        jobID = 0,
        exec = $bindable({}),
    } = $props();

    interface logLineType {
        nr: number,
        content: string,
    }

    const classText = 'text-base text-wrap';
    const classProp = 'font-bold text-base pr-3';
    const endDiv = `logs-end-${jobID}-${exec.id}`;

    let apiResponseHandler: APIResponseHandler = $state();
    let updateLoop: number = $state(0);
    let lastLogLine: number = $state(0);
    let logLines: logLineType[] = $state([]);
    let finished = $state(false);
    let lineNr = $state(1);
    let apiSuccessMsg = $state('');
    let followLogsToggle = $state(true);

    function t(code: string) : string {
        return tq($share, code);
    }

    function followLogs() {
        if (!followLogsToggle) {
            return;
        }
        let e = document.getElementById(endDiv);
        if (e) {
            e.scrollIntoView({behavior: "smooth", block: "end", inline: "end"});
        }
    }

    function loadLogLines(j: any) {
        if (!j || !j.lines) {
            return;
        }
        let newLogLines = [...logLines];
        for (let l of j.lines) {
            newLogLines.push({nr: lineNr, content: l});
            lineNr += 1;
        }
        lastLogLine = lineNr;
        logLines = newLogLines;
        followLogs();
        if (lastLogLine >= j.count && j.finished) {
            finished = true;
        }
    }

    function stopJob() {
        apiSuccessMsg = 'jobs.action.stop';
        apiEdit('delete', `job/${jobID}/${exec.id}`, null, apiResponseHandler.handleRes);
    }

    function isExecActive() : boolean {
        return JOB_EXEC_STATI_ACTIVE.includes(exec.status);
    }

    function buildUpdateLogsList() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        if (finished || exec.failed || !isExecActive) {
            return;
        }
        apiGet(`job/${jobID}/${exec.id}/log/${lastLogLine}`, loadLogLines);
    }

    onMount(() => {
        buildUpdateLogsList();

        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            buildUpdateLogsList();
        }, $share.updateInterval);
    });

    onDestroy(()=>{
    	clearInterval(updateLoop);
    });
</script>

<APIResponseHandler bind:this={apiResponseHandler} bind:successMsg={apiSuccessMsg} />

<Modal bind:open={open} size="lg" autoclose={false} placement="top-center" backdropClass={classModalBackdrop}>
    <Heading tag="h2">{t('logs.job_logs')} "{jobName}"</Heading>
    {#if exec.failed}
        <div class="mt-20 mb-10 font-bold text-lg {classCenterChildDiv}">
            <CloseCircleSolid class="inline-block mr-2" /> {t('logs.exec_failed')}
        </div>
        {#if exec.error_s}
            <Alert color="red" class="mx-10 my-5">
                <div class="font-bold text-lg mb-3">{t('logs.error_short')}</div>
                <div>{exec.error_s}</div>
            </Alert>
        {/if}
        {#if exec.error_m}
            <Alert color="red" class="mx-10 my-5">
                <div class="font-bold text-lg mb-3">{t('logs.error_medium')}</div>
                <pre class="whitespace-pre-wrap break-normal">{exec.error_m}</pre>
            </Alert>
        {/if}
    {:else if !logLines.length}
        <div class={classSpinnerDiv}><Spinner/></div>
    {:else}
        <table>
            <tbody>
                <tr>
                    <td class={classProp}>{t('logs.command')}:</td>
                    <td class={classText}>{exec.command}</td>
                </tr>
                <tr>
                    <td class={classProp}>{t('logs.time_start')}:</td>
                    <td class={classText}>{exec.time_start}</td>
                </tr>
                <tr>
                    <td class={classProp}>{t('logs.executed_by')}:</td>
                    <td class={classText}>{exec.user_name}</td>
                </tr>
                {#if exec.comment}
                    <tr>
                        <td class={classProp}>{t('jobs.form.comment')}:</td>
                        <td class={classText}>{exec.comment}</td>
                    </tr>
                {/if}
                <tr>
                    <td class={classProp}>{t('logs.exec_log_file')}:</td>
                    <td class={classText}>
                        <a href="{exec.log_stdout_url}">{exec.log_stdout}</a>
                    </td>
                </tr>
                {#if exec.log_sderr}
                    <tr>
                        <td class={classProp}>{t('logs.exec_error_log_file')}:</td>
                        <td class={classText}>
                            <a href="{exec.log_sderr_url}">{exec.log_sderr}</a>
                        </td>
                    </tr>
                {/if}
                {#if exec.log_stdout_repo}
                    <tr>
                        <td class={classProp}>{t('logs.repo_log_file')}:</td>
                        <td class={classText}>
                            <a href="{exec.log_stdout_repo_url}">{exec.log_stdout_repo}</a>
                        </td>
                    </tr>
                {/if}
                {#if exec.log_stderr_repo}
                    <tr>
                        <td class={classProp}>{t('logs.repo_error_log_file')}:</td>
                        <td class={classText}>
                            <a href="{exec.log_stderr_repo_url}">{exec.log_stderr_repo}</a>
                        </td>
                    </tr>
                {/if}
            </tbody>
        </table>
        <table>
            <tbody>
                <!-- todo: add internal error messages -->
                {#each logLines as line (line.nr)}
                    <tr>
                        <td class="pr-3">{line.nr}</td>
                        <td class="whitespace-pre-wrap break-words {classText}">{@html line.content}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
        {#if finished}
            <div class="mt-20 mb-10 font-bold text-lg {classCenterChildDiv}">
                <InfoCircleSolid class="inline-block mr-2" /> {t('logs.exec_finished')}
            </div>
        {/if}
        <div class="h-28"></div>
        <div id={endDiv} class="w-0 h-0"></div>
    {/if}
    <div class="fixed bottom-10 right-96">
        <div class={classCenterChildDiv}>
            <Button id="logs-btn-close" on:click={() => (open = false)}>
                <CloseCircleSolid/>
            </Button>
            <Tooltip>{t('btn.close')}</Tooltip>

            {#if isExecActive()}
                <div class="inline-block ml-2 {classCenterChildDiv}">
                    <Toggle id="logs-btn-pause" bind:checked={followLogsToggle} />
                    <Tooltip>{t('btn.pause')}</Tooltip>
                </div>

                <Button id="logs-btn-stop" on:click={() => {stopJob()}} class="ml-2">
                    <StopSolid/>
                </Button>
                <Tooltip>{t('btn.stop')}</Tooltip>
            {/if}
        </div>
    </div>
</Modal>
