import { SvelteComponentTyped } from "svelte";
import type { SizeType, FormSizeType } from '../types';
export declare function clampSize(s: SizeType): "sm" | "lg" | "md";
import type { HTMLInputAttributes } from 'svelte/elements';
import type { InputType } from '../types';
declare const __propDef: {
    props: Omit<HTMLInputAttributes, "size"> & {
        type?: InputType;
        value?: any;
        size?: FormSizeType;
        clearable?: boolean;
        defaultClass?: string;
        color?: "base" | "green" | "red";
        floatClass?: string;
        classLeft?: string;
        classRight?: string;
        placeholder?: string;
        disabled?: boolean;
        separators?: [];
        validationCallback?: CallableFunction,
        validationErrorClass?: string,
    };
    events: {
        blur: FocusEvent;
        change: CustomEvent<any>;
        click: MouseEvent;
        contextmenu: MouseEvent;
        focus: FocusEvent;
        keydown: KeyboardEvent;
        keypress: KeyboardEvent;
        keyup: KeyboardEvent;
        mouseover: MouseEvent;
        mouseenter: MouseEvent;
        mouseleave: MouseEvent;
        paste: ClipboardEvent;
        input: Event;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        left: {};
        default: {
            props: {
                class: string;
            };
        };
        right: {};
    };
};
export type InputProps = typeof __propDef.props;
export type InputEvents = typeof __propDef.events;
export type InputSlots = typeof __propDef.slots;
/**
 * [Go to docs](https://flowbite-svelte.com/)
 * ## Props
 * @prop export let type: $$Props['type'] = 'text';
 * @prop export let value: $$Props['value'] = undefined;
 * @prop export let size: $$Props['size'] = undefined;
 * @prop export let clearable: $$Props['clearable'] = false;
 * @prop export let defaultClass: $$Props['defaultClass'] = 'block w-full disabled:cursor-not-allowed disabled:opacity-50 rtl:text-right';
 * @prop export let color: NonNullable<$$Props['color']> = 'base';
 * @prop export let floatClass: $$Props['floatClass'] = 'flex absolute inset-y-0 items-center text-gray-500 dark:text-gray-400';
 * @prop export let classLeft: $$Props['classLeft'] = '';
 * @prop export let classRight: $$Props['classRight'] = '';
 */
export default class Input extends SvelteComponentTyped<InputProps, InputEvents, InputSlots> {
}
export {};
