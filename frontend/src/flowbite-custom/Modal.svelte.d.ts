import { SvelteComponentTyped } from "svelte";
import type { Dismissable, SizeType } from '../types';
import type { ModalPlacementType } from '../types';
declare const __propDef: {
    props: import("svelte/elements").HTMLAnchorAttributes & {
        tag?: string;
        color?: import("../utils/Frame.svelte").FrameColor;
        rounded?: boolean;
        border?: boolean;
        shadow?: boolean;
        node?: HTMLElement | undefined;
        use?: import("svelte/action").Action<HTMLElement, any>;
        options?: object;
        class?: string;
        role?: string;
        open?: boolean;
        transition?: (node: HTMLElement, params: any) => import("svelte/transition").TransitionConfig;
        params?: any;
    } & Dismissable & {
        open?: boolean;
        title?: string;
        size?: SizeType;
        placement?: ModalPlacementType;
        autoclose?: boolean;
        outsideclose?: boolean;
        backdropClass?: string;
        classBackdrop?: string;
        dialogClass?: string;
        classDialog?: string;
        defaultClass?: string;
        headerClass?: string;
        classHeader?: string;
        bodyClass?: string;
        classBody?: string;
        footerClass?: string;
        classFooter?: string;
    };
    events: {
        wheel: WheelEvent;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        header: {};
        default: {};
        footer: {};
    };
};
export type ModalProps = typeof __propDef.props;
export type ModalEvents = typeof __propDef.events;
export type ModalSlots = typeof __propDef.slots;
/**
 * [Go to docs](https://flowbite-svelte.com/)
 * ## Props
 * @prop export let open: $$Props['open'] = false;
 * @prop export let title: $$Props['title'] = '';
 * @prop export let size: NonNullable<$$Props['size']> = 'md';
 * @prop export let color: $$Props['color'] = 'default';
 * @prop export let placement: NonNullable<$$Props['placement']> = 'center';
 * @prop export let autoclose: $$Props['autoclose'] = false;
 * @prop export let outsideclose: $$Props['outsideclose'] = false;
 * @prop export let dismissable: $$Props['dismissable'] = true;
 * @prop export let backdropClass: $$Props['backdropClass'] = 'fixed inset-0 z-40 bg-gray-900 bg-opacity-50 dark:bg-opacity-80';
 * @prop export let classBackdrop: $$Props['classBackdrop'] = undefined;
 * @prop export let dialogClass: $$Props['dialogClass'] = 'fixed top-0 start-0 end-0 h-modal md:inset-0 md:h-full z-50 w-full p-4 flex';
 * @prop export let classDialog: $$Props['classDialog'] = undefined;
 * @prop export let defaultClass: $$Props['defaultClass'] = 'relative flex flex-col mx-auto';
 * @prop export let headerClass: $$Props['headerClass'] = 'flex justify-between items-center p-4 md:p-5 rounded-t-lg';
 * @prop export let classHeader: $$Props['classHeader'] = undefined;
 * @prop export let bodyClass: $$Props['bodyClass'] = 'p-4 md:p-5 space-y-4 flex-1 overflow-y-auto overscroll-contain';
 * @prop export let classBody: $$Props['classBody'] = undefined;
 * @prop export let footerClass: $$Props['footerClass'] = 'flex items-center p-4 md:p-5 space-x-3 rtl:space-x-reverse rounded-b-lg';
 * @prop export let classFooter: $$Props['classFooter'] = undefined;
 */
export default class Modal extends SvelteComponentTyped<ModalProps, ModalEvents, ModalSlots> {
}
export {};
