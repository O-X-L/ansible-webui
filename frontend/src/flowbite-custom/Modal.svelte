<script lang="ts">
  import { twMerge } from "tailwind-merge";
  import Frame from "../../node_modules/flowbite-svelte/dist/utils/Frame.svelte";
  import { createEventDispatcher } from "svelte";
  import CloseButton from "../../node_modules/flowbite-svelte/dist/utils/CloseButton.svelte";
  import focusTrap from "../../node_modules/flowbite-svelte/dist/utils/focusTrap";
  export let open = false;
  export let title = "";
  export let size = "md";
  export let color = "default";
  export let placement = "center";
  export let autoclose = false;
  export let outsideclose = false;
  export let dismissable = true;
  export let backdropClass = "fixed inset-0 z-40 bg-gray-900 bg-opacity-50 dark:bg-opacity-80";
  export let classBackdrop = void 0;
  export let dialogClass = "fixed top-0 start-0 end-0 h-modal md:inset-0 md:h-full z-50 w-full p-4 flex";
  export let classDialog = void 0;
  export let defaultClass = "relative flex flex-col mx-auto";
  export let headerClass = "flex justify-between items-center p-4 md:p-5 rounded-t-lg";
  export let classHeader = void 0;
  export let bodyClass = "p-4 md:p-5 space-y-4 flex-1 overflow-y-auto overscroll-contain";
  export let classBody = void 0;
  export let footerClass = "flex items-center p-4 md:p-5 space-x-3 rtl:space-x-reverse rounded-b-lg";
  export let classFooter = void 0;
  const dispatch = createEventDispatcher();
  $: dispatch(open ? "open" : "close");
  function prepareFocus(node) {
    const walker = document.createTreeWalker(node, NodeFilter.SHOW_ELEMENT);
    let n;
    while (n = walker.nextNode()) {
      if (n instanceof HTMLElement) {
        const el = n;
        const [x, y] = isScrollable(el);
        if (x || y) el.tabIndex = 0;
      }
    }
    node.focus();
  }
  const getPlacementClasses = (placement2) => {
    switch (placement2) {
      case "top-left":
        return ["justify-start", "items-start"];
      case "top-center":
        return ["justify-center", "items-start"];
      case "top-right":
        return ["justify-end", "items-start"];
      case "center-left":
        return ["justify-start", "items-center"];
      case "center":
        return ["justify-center", "items-center"];
      case "center-right":
        return ["justify-end", "items-center"];
      case "bottom-left":
        return ["justify-start", "items-end"];
      case "bottom-center":
        return ["justify-center", "items-end"];
      case "bottom-right":
        return ["justify-end", "items-end"];
      default:
        return ["justify-center", "items-center"];
    }
  };
  const sizes = {
    xs: "max-w-md",
    sm: "max-w-lg",
    md: "max-w-2xl",
    lg: "max-w-4xl",
    xl: "max-w-7xl"
  };
  const onAutoClose = (e) => {
    const target = e.target;
    if (autoclose && target?.tagName === "BUTTON") hide(e);
  };
  const onOutsideClose = (e) => {
    const target = e.target;
    if (outsideclose && target === e.currentTarget) hide(e);
  };
  const hide = (e) => {
    e.preventDefault();
    open = false;
  };
  const isScrollable = (e) => [e.scrollWidth > e.clientWidth && ["scroll", "auto"].indexOf(getComputedStyle(e).overflowX) >= 0, e.scrollHeight > e.clientHeight && ["scroll", "auto"].indexOf(getComputedStyle(e).overflowY) >= 0];
  function handleKeys(e) {
    if (e.key === "Escape" && dismissable) return hide(e);
  }
  $: backdropCls = twMerge(backdropClass, classBackdrop);
  $: dialogCls = twMerge(dialogClass, classDialog, getPlacementClasses(placement));
  $: frameCls = twMerge(defaultClass, "w-full divide-y", $$props.class);
  $: headerCls = twMerge(headerClass, classHeader);
  $: bodyCls = twMerge(bodyClass, classBody);
  $: footerCls = twMerge(footerClass, classFooter);
</script>

{#if open}
  <!-- backdrop -->
  <div class={backdropCls}></div>
  <!-- dialog -->
  <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
  <div on:keydown={handleKeys} on:wheel|preventDefault|nonpassive use:prepareFocus use:focusTrap on:click={onAutoClose} on:mousedown={onOutsideClose} class={dialogCls} tabindex="-1" aria-modal="true" role="dialog">
    <div class="flex relative {sizes[size]} w-full max-h-screen">
      <!-- Modal content -->
      <Frame rounded shadow {...$$restProps} class={frameCls} {color}>
        <!-- Modal header -->
        {#if $$slots.header || title}
          <Frame class={headerCls} {color}>
            <slot name="header">
              <h3 class="text-xl font-semibold {color === 'default' ? '' : 'text-gray-900 dark:text-white'} p-0">
                {title}
              </h3>
            </slot>
            {#if dismissable}<CloseButton name="Close modal" {color} on:click={hide} />{/if}
          </Frame>
        {/if}
        <!-- Modal body -->
        <div class={bodyCls} role="document" on:keydown|stopPropagation={handleKeys} on:wheel|stopPropagation|passive>
          {#if dismissable && !$$slots.header && !title}
            <CloseButton name="Close modal" class="absolute top-3 end-2.5" {color} on:click={hide} />
          {/if}
          <slot></slot>
        </div>
        <!-- Modal footer -->
        {#if $$slots.footer}
          <Frame class={footerCls} {color}>
            <slot name="footer"></slot>
          </Frame>
        {/if}
      </Frame>
    </div>
  </div>
{/if}

<!--
@component
[Go to docs](https://flowbite-svelte.com/)
## Props
@prop export let open: $$Props['open'] = false;
@prop export let title: $$Props['title'] = '';
@prop export let size: NonNullable<$$Props['size']> = 'md';
@prop export let color: $$Props['color'] = 'default';
@prop export let placement: NonNullable<$$Props['placement']> = 'center';
@prop export let autoclose: $$Props['autoclose'] = false;
@prop export let outsideclose: $$Props['outsideclose'] = false;
@prop export let dismissable: $$Props['dismissable'] = true;
@prop export let backdropClass: $$Props['backdropClass'] = 'fixed inset-0 z-40 bg-gray-900 bg-opacity-50 dark:bg-opacity-80';
@prop export let classBackdrop: $$Props['classBackdrop'] = undefined;
@prop export let dialogClass: $$Props['dialogClass'] = 'fixed top-0 start-0 end-0 h-modal md:inset-0 md:h-full z-50 w-full p-4 flex';
@prop export let classDialog: $$Props['classDialog'] = undefined;
@prop export let defaultClass: $$Props['defaultClass'] = 'relative flex flex-col mx-auto';
@prop export let headerClass: $$Props['headerClass'] = 'flex justify-between items-center p-4 md:p-5 rounded-t-lg';
@prop export let classHeader: $$Props['classHeader'] = undefined;
@prop export let bodyClass: $$Props['bodyClass'] = 'p-4 md:p-5 space-y-4 flex-1 overflow-y-auto overscroll-contain';
@prop export let classBody: $$Props['classBody'] = undefined;
@prop export let footerClass: $$Props['footerClass'] = 'flex items-center p-4 md:p-5 space-x-3 rtl:space-x-reverse rounded-b-lg';
@prop export let classFooter: $$Props['classFooter'] = undefined;
-->
