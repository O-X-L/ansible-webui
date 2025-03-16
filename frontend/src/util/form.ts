import { apiEdit, getCSRFFormTokenJSON } from './api.js';
import { type inputColor, type toggleColor } from '../base/Types.js';

export const inputBaseColor: inputColor = 'base';
export const inputRequiredBaseColor: inputColor = 'red';
export const toggleBaseColor: toggleColor = undefined;

export const REGEX_SMALL_INT = /^[\d]{1,3}$/
export const REGEX_INT = /^[\d]{1,10}$/

export interface formField {
    value: string|number|boolean,
    regex: RegExp|undefined,
    color: inputColor|toggleColor,
    required: boolean|undefined,
    blank: boolean|undefined,
}

export type formMethod = 'post' | 'put' | 'delete';

export function validateFormField(field: formField) {
    if (field.required !== undefined && field.required && !field.value) {
        return false;
    }

    if (field.regex !== undefined) {
        return field.regex.test(String(field.value));
    }

    return true;
}

export function valideInputBase(e: Event, form: any) {
    let k = e.target.name;
    let v: formField = form[k];
    if ((v.required === undefined || !v.required || (v.required && v.value)) &&
    ((v.blank !== undefined && v.blank && v.value == '') || validateFormField(v))) {
        v.color = inputBaseColor;

    } else {
        v.color = 'red';
    }
}

export function submitFormBase(form: any, method: formMethod, url: string, callback: CallableFunction) {
    let payload = {...getCSRFFormTokenJSON()};
    let valid = true;

    for (let [k, v] of Object.entries(form)) {
        if (!validateFormField(v)) {
            // todo: give error message (?)
            v.color = 'red';
            valid = false;

        }
        payload[k] = v.value;
    }
    if (valid) {
        console.log("SUBMITTING FORM", payload);
        apiEdit(method, url, payload, callback);
    }
}

