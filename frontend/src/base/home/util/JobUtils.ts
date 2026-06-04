import { redirectTo } from '../../../util/main.js';
import { URL_HASH_PARAM_SEPARATOR, URL_HASH_PARAM_KV } from '../../../util/main.js';

export function redirectLogs(jobId: number) {
    if (!jobId) {
        return;
    }
    redirectTo(`/ui#logs${URL_HASH_PARAM_SEPARATOR}job${URL_HASH_PARAM_KV}${jobId}`);
}
