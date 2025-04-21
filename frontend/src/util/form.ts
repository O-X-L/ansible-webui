import { TT } from './translate.js';
import { apiEdit, getCSRFFormTokenJSON } from './api.js';
import { type inputColorType, type formChoiceType } from '../base/Types.js';

export const inputBaseColor: inputColorType = 'base';
export const inputRequiredBaseColor: inputColorType = 'red';

export const REGEX_SMALL_INT = /^[\d]{1,3}$/
export const REGEX_INT = /^[\d]{1,10}$/

export interface formField {
    value: string|number|boolean,
    regex: RegExp|undefined,
    color: inputColorType,
    required: boolean|undefined,
    blank: boolean|undefined,
}

export type formMethod = 'post' | 'put' | 'delete';

export function validateFormField(field: formField) : boolean {
    if (field.required !== undefined && field.required && !field.value) {
        return false;
    }

    if (field.regex !== undefined) {
        return field.regex.test(String(field.value));
    }

    return true;
}

export function valideInputBase(e: Event, i: any|formField) {
    let k = e.target.name;
    let v: formField;
    if (!i[k]) {
        v = i;
    } else {
        v = i[k];
    }
    if ((v.required === undefined || !v.required || (v.required && v.value)) &&
    ((v.blank !== undefined && v.blank && v.value == '') || validateFormField(v))) {
        v.color = inputBaseColor;

    } else {
        v.color = 'red';
    }
}

export function submitFormBase(
    form: any, method: formMethod, url: string, callback: CallableFunction,
    t: CallableFunction, tb: string,
    ignoreFields: string[] = [], ignoreFieldsValidate: string[] = [],
) : [boolean, string[]] {
    let payload = {...getCSRFFormTokenJSON()};
    let valid = true;
    let validationErrors : string[] = [];

    for (let [k, v] of Object.entries(form)) {
        if (ignoreFields.includes(k)) {
            continue;
        }
        if (!ignoreFieldsValidate.includes(k) && !validateFormField(v)) {
            let e = `${t('common.invalid_value')}: "${tb}${k}"`
            console.log(`ERROR: ${e}`);
            validationErrors.push(e + TT);
            v.color = 'red';
            valid = false;
        }
        payload[k] = v.value;
    }
    if (valid) {
        console.log("SUBMITTING FORM");  // payload
        apiEdit(method, url, payload, callback);
    }
    return [valid, validationErrors];
}

export function choicesFromArray(a: string[]) : formChoiceType[] {
    let c: formChoiceType[] = [];
    for (let i of a) {
        c.push({'value': i, 'name': i})
    }
    return c
}

export function getMethod(a: string) : 'post'|'put'|'delete' {
    if (a == 'delete') {
        return 'delete';
    }
    if (a == 'edit') {
        return 'put';
    }
    return 'post';
}
