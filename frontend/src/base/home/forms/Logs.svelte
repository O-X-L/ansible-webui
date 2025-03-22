<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { InfoCircleSolid } from 'flowbite-svelte-icons';
    import { Spinner, Modal, Heading } from 'flowbite-svelte';

    import { share } from '../../Share.js';
    import { apiGet } from '../../../util/api.js';
    import { tq } from '../../../util/translate.js';
    // import { type executionType } from '../Types.js';
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

    function t(code: string) : string {
        return tq($share, code);
    }

    function followLogs() {
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

    function buildUpdateLogsList() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        if (finished) {
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

<APIResponseHandler bind:this={apiResponseHandler} />

<Modal bind:open={open} size="lg" autoclose={false} placement="top-center" backdropClass={classModalBackdrop}>
    <Heading tag="h2">{t('logs.job_logs')} "{jobName}"</Heading>
    {#if !logLines.length}
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
</Modal>
