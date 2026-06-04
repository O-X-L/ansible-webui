<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { init, use, type ECharts } from 'echarts/core';
    import type { ComposeOption } from 'echarts/core';
    import { LineChart } from 'echarts/charts';
    import {
        GridComponent,
        TooltipComponent,
        LegendComponent,
        TitleComponent,
        DatasetComponent,
    } from 'echarts/components';
    import type { LineSeriesOption } from 'echarts/charts';
    import type {
        GridComponentOption,
        TooltipComponentOption,
        LegendComponentOption,
        TitleComponentOption,
        DatasetComponentOption,
    } from 'echarts/components';
    import { CanvasRenderer } from 'echarts/renderers';

    use([
        TitleComponent,
        GridComponent,
        TooltipComponent,
        LegendComponent,
        DatasetComponent,
        LineChart,
        CanvasRenderer
    ]);
    type EChartsOption = ComposeOption<
        | LineSeriesOption
        | GridComponentOption
        | TitleComponentOption
        | TooltipComponentOption
        | LegendComponentOption
        | DatasetComponentOption
        | TooltipComponentOption
        | LegendComponentOption
        | TitleComponentOption
    >;


    import { share } from '../../Share.js';
    import { tq } from '../../../util/translate.js';
    import { getDarkLightMode } from '../../DarkLightMode.js';
    import type { statsJobs, statsExecution } from '../Types.js';
    import { arraysEqual, hashString } from '../../../util/main.js';
    import { CHART_COLOR_SUCCESS, CHART_COLOR_FAILED } from '../../../util/colors.js'; //

    let { data }: { data: statsJobs } = $props();

    let chartContainer: HTMLElement;
    let execOverTimeChart: ECharts | null = null;
    let chartDataExecOverTimeJobs: string[] = $state([]);

    const TIME_FORMAT = 'h23';
    const CHART_TIME_MAX_DATAPOINTS = 125;
    const GROUP_SUCCESS_KEY = 'GROUP_SUCCESS';
    const GROUP_FAILED_KEY = 'GROUP_FAILED';
    const HIGHLIGHT_COLOR_LIGHT = '#3B82F6';
    const HIGHLIGHT_COLOR_DARK = '#22D3EE';

    const SUCCESS_HUE_START = 160; // Green/Cyan
    const SUCCESS_HUE_END = 240;   // Blue (avoids pink/violet/red-ish hues > 280)
    const FAILED_HUE = 27;         // Red
    const CHROMA_BASE = 0.20;      // Base saturation

    /**
     * Deterministically generates a unique OKLCH color for a job name.
     * Varies Luminosity and Hue for better distinction and contrast.
     */
    function getJobColor(jobName: string, isFailed: boolean, isDark: boolean): string {
        const hash = hashString(jobName) / 4294967296; // [0, 1] 
        
        let luminosity;
        let hue;
        let chroma;
        
        if (isFailed) {
            hue = FAILED_HUE;
            const L_RED_MIN = isDark ? 0.50 : 0.35;
            const L_RED_MAX = isDark ? 0.80 : 0.65;
            const L_RED_RANGE = L_RED_MAX - L_RED_MIN;
            luminosity = L_RED_MIN + (hash * L_RED_RANGE); 
            chroma = CHROMA_BASE + (hash * 0.20); 
            if (chroma > 0.40) chroma = 0.40;
            
        } else {
            const L_SUCCESS_RANGE = 0.20; 
            if (isDark) {
                luminosity = 0.60 + (hash * L_SUCCESS_RANGE); // [0.60, 0.80]
            } else {
                luminosity = 0.40 + (hash * L_SUCCESS_RANGE); // [0.40, 0.60]
            }
            const HUE_RANGE = SUCCESS_HUE_END - SUCCESS_HUE_START;
            hue = SUCCESS_HUE_START + (hash * HUE_RANGE);
            chroma = CHROMA_BASE;
        }
        
        return `oklch(${luminosity.toFixed(3)} ${chroma.toFixed(3)} ${hue.toFixed(3)})`;
    }
    
    function t(code: string) : string {
        return tq($share, code);
    }

    /**
     * Converts raw execution data into an ECharts-friendly series array format.
     * @returns {[boolean, any[]]} [data_changed_flag, ECharts Series Array with custom property]
     */
    function getExecOverTimeData(): [boolean, any[]] {
        let jobs_success: { [key: string]: number[][] } = {};
        let jobs_failed: { [key: string]: number[][] } = {};

        let i = 0;
        const isDark = getDarkLightMode() == 'dark';

        for (let s of data['stats'] as statsExecution[]) {
            if (i > CHART_TIME_MAX_DATAPOINTS) {
                break;
            }
            let n = data['mapping']['jobs'][s[0]];
            if (!jobs_success[n]) {
                jobs_success[n] = [];
                jobs_failed[n] = [];
            }
            if (!s[4] || s[4] === 0) {
                continue;
            }
            
            // dataPoint format: [time (ms), duration (s)]
            const dataPoint: [number, number] = [Math.round(s[4]) * 1000, s[3]];
            if (s[5] === 1) { // 5 is 'failed (0/1 boolean)'
                jobs_failed[n].push(dataPoint);
            } else {
                jobs_success[n].push(dataPoint);
            }
            i += 1;
        }

        let dataset_keys: string[] = [];
        let series: any[] = [];
        const defaults: Partial<LineSeriesOption> = {
            type: 'line', 
            symbol: 'circle',
            symbolSize: 15,
            lineStyle: {
                width: 0,
            },
            animation: false, 
        };

        for (let [jobName, dataPoints] of Object.entries(jobs_success)) {
            const seriesName = jobName;
            const color = getJobColor(jobName, false, isDark);
            
            series.push({
                name: seriesName,
                id: `${jobName}-success`,
                data: dataPoints,
                itemStyle: {
                    color: color,
                },
                jobGroup: GROUP_SUCCESS_KEY,
                ...defaults,
            });
            dataset_keys.push(seriesName);
        }

        for (let [jobName, dataPoints] of Object.entries(jobs_failed)) {
            const seriesName = `${jobName} `;
            const color = getJobColor(jobName, true, isDark);
            
            series.push({
                name: seriesName,
                id: `${jobName}-failed`,
                data: dataPoints,
                itemStyle: {
                    color: color,
                },
                jobGroup: GROUP_FAILED_KEY,
                ...defaults,
            });
            dataset_keys.push(seriesName);
        }
        
        const changed = !arraysEqual(dataset_keys.sort(), chartDataExecOverTimeJobs.sort());
        if (changed) {
            chartDataExecOverTimeJobs = dataset_keys;
        }
        
        return [changed, series];
    }

    /**
     * Initializes the ECharts instance and sets up the chart options.
     */
    function addExecOverTimeChart() {
        const isDark = getDarkLightMode() == 'dark';
        const textColor = isDark ? '#ADBABD' : '#333';
        
        if (!chartContainer) return;
        execOverTimeChart = init(chartContainer, isDark ? 'dark' : 'light');
        const [_, individualSeries] = getExecOverTimeData();
        const highlightColor = isDark ? HIGHLIGHT_COLOR_DARK : HIGHLIGHT_COLOR_LIGHT;
        const GROUP_SUCCESS_NAME = t('jobs.info.succeeded');
        const GROUP_FAILED_NAME = t('jobs.info.failed');

        const updatedIndividualSeries = individualSeries.map(s => ({
            ...s,
            emphasis: {
                focus: 'self',
                itemStyle: {
                    color: highlightColor, 
                    borderColor: highlightColor,
                    borderWidth: 2,
                },
                lineStyle: {
                    width: 2,
                    color: highlightColor,
                },
                symbol: 'circle',
                symbolSize: 20
            }
        }));
        
        // Restored grouping series
        const groupSeries = [
            { name: GROUP_SUCCESS_NAME, type: 'line', data: [], symbol: 'none', lineStyle: { width: 0 }, itemStyle: { color: CHART_COLOR_SUCCESS }, jobGroup: GROUP_SUCCESS_KEY },
            { name: GROUP_FAILED_NAME, type: 'line', data: [], symbol: 'none', lineStyle: { width: 0 }, itemStyle: { color: CHART_COLOR_FAILED }, jobGroup: GROUP_FAILED_KEY },
        ];
        const allSeries = groupSeries.concat(updatedIndividualSeries);
        
        const option: EChartsOption = {
            title: {
                // text: t('db.chart.exec_over_time'),
                left: 'center',
                textStyle: {
                    color: textColor
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '10%',           
                containLabel: true
            },
            backgroundColor: 'transparent',
            /*
            tooltip: {
                axisPointer: { 
                   type: 'cross',
                },
                trigger: 'axis',
                formatter: function (params) {
                    if (!params) {
                        return '';
                    }
                    return JSON.stringify([params.map(p => p.value)])
                }
            },
            */
            legend: {
                show: true,
                orient: 'horizontal',
                bottom: '0%',
                textStyle: {
                    color: textColor
                },
                data: allSeries.map(s => s.name),
                selected: Object.fromEntries(allSeries.map(s => [s.name, true])),
            },
            xAxis: {
                type: 'time',
                name: t('logs.time'),
                nameLocation: 'middle',
                nameGap: 30,
                axisLabel: {
                    formatter: {
                        year: '{yyyy}',
                        month: '{MMM}',
                        day: '{d}',
                        hour: '{HH}:{mm}',
                        minute: '{HH}:{mm}',
                        second: '{HH}:{mm}:{ss}'
                    },
                    color: textColor
                },
                splitLine: {
                    show: false
                }
            },
            yAxis: {
                type: 'value',
                name: t('jobs.info.duration'),
                nameLocation: 'middle',
                nameGap: 50,
                min: 0, 
                axisLabel: {
                    formatter: '{value} s',
                    color: textColor
                },
                splitLine: {
                    lineStyle: {
                        color: isDark ? '#333' : '#eee'
                    }
                }
            },
            series: allSeries
        };
        execOverTimeChart.setOption(option);

        execOverTimeChart.on('legendselectchanged', (params: any) => {
            if (!execOverTimeChart) {
                return;
            }
            const name = params.name;
            if (name === GROUP_SUCCESS_NAME || name === GROUP_FAILED_NAME) {
                const isSelected = params.selected[name];
                const groupKey = name === GROUP_SUCCESS_NAME ? GROUP_SUCCESS_KEY : GROUP_FAILED_KEY;
                updatedIndividualSeries.forEach(s => {
                    if (s.jobGroup === groupKey) {
                        execOverTimeChart.dispatchAction({
                            type: isSelected ? 'legendSelect' : 'legendUnSelect',
                            name: s.name,
                        });
                    }
                });
            }
        });
        window.addEventListener('resize', resizeChart);
    }

    /**
     * Resizes the ECharts instance on window resize.
     */
    function resizeChart() {
        execOverTimeChart?.resize();
    }

    /**
     * Updates the chart data, and refreshes the chart.
     */
    function createUpdateChart() {
        if (!execOverTimeChart) {
            addExecOverTimeChart();
            return;
        }
        
        const [changed, newIndividualSeries] = getExecOverTimeData();
        const isDark = getDarkLightMode() == 'dark';
        const highlightColor = isDark ? HIGHLIGHT_COLOR_DARK : HIGHLIGHT_COLOR_LIGHT;
        const GROUP_SUCCESS_NAME = t('jobs.info.succeeded');
        const GROUP_FAILED_NAME = t('jobs.info.failed');

        const updatedNewIndividualSeries = newIndividualSeries.map(s => {
            return {
                ...s,
                emphasis: {
                    focus: 'self',
                    itemStyle: {
                        color: highlightColor,
                        borderColor: highlightColor,
                        borderWidth: 2,
                    },
                    lineStyle: {
                        width: 2,
                        color: highlightColor,
                    },
                    symbol: 'circle',
                    symbolSize: 20,
                },
            }
        });
        
        const groupSeries = [
            { name: GROUP_SUCCESS_NAME, type: 'line', data: [] },
            { name: GROUP_FAILED_NAME, type: 'line', data: [] },
        ];
        const finalNewSeries = updatedNewIndividualSeries.concat(groupSeries);

        if (changed) {
            execOverTimeChart.setOption({
                series: finalNewSeries,
                legend: {
                    data: finalNewSeries.map(s => s.name),
                    selected: Object.fromEntries(finalNewSeries.map(s => [s.name, true])),
                }
            }, true);
        } else {
            execOverTimeChart.setOption({
                series: finalNewSeries.map(series => ({
                    name: series.name, 
                    data: series.data
                }))
            }, false);
        }
    }

    $effect(() => {
        data;
        createUpdateChart();
    });
    onMount(() => {
        addExecOverTimeChart();
    });
    onDestroy(() => {
        window.removeEventListener('resize', resizeChart);
        execOverTimeChart?.dispose();
    });
</script>

<div bind:this={chartContainer} id="chart-exec-over-time" class="h-96 w-full" role="img" aria-label="{t('db.chart.exec_over_time')} Chart"></div>