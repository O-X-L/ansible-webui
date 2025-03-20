<script lang="ts">
    import { Spinner, Accordion, AccordionItem } from 'flowbite-svelte';

    import { share } from '../Share.js';
    import { tq } from '../../util/translate.js';
    import { classSpinnerDiv } from '../Style.js';

    let { open = $bindable(false) } = $props();

    function t(code: string) : string {
      return tq($share, code);
    }
</script>

<Accordion>
    <AccordionItem>
        <span slot="header">Setting Category 1</span>
        <div class={classSpinnerDiv}><Spinner/></div>
    </AccordionItem>
</Accordion>
