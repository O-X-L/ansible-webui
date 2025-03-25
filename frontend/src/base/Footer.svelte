<script lang="ts">
    import { sineIn } from 'svelte/easing';

    import {
      Footer, FooterCopyright, FooterLinkGroup, Spinner, Drawer, CloseButton, Listgroup,
    } from 'flowbite-svelte';

    import { share } from './Share.js';
    import { tq } from '../util/translate.js';
    import { classNavFooter, classLinkHover } from './Style.js';

    const classFooterText = 'text-sm max-sm:text-xs text-gray-500 dark:text-gray-400';
    let hideAttributions = $state(true);

    let linksAttributionFrontend = [
        { name: 'Svelte', href: 'https://svelte.dev/', license: 'MIT', licenseHref: 'https://github.com/sveltejs/svelte/blob/main/LICENSE.md'},
        { name: 'Tailwind CSS', href: 'https://tailwindcss.com/', license: 'MIT', licenseHref: 'https://github.com/tailwindlabs/tailwindcss/blob/main/LICENSE' },
        { name: 'Flowbite Svelte', href: 'https://flowbite-svelte.com/', license: 'MIT', licenseHref: 'https://flowbite-svelte.com/docs/pages/license' },
        { name: 'Chart.js', href: 'https://www.chartjs.org/', license: 'MIT', licenseHref: 'https://github.com/chartjs/Chart.js/blob/master/LICENSE.md' },
        { name: 'date-fns', href: 'https://date-fns.org/', license: 'MIT', licenseHref: 'https://github.com/date-fns/date-fns/blob/main/LICENSE.md' },
        { name: 'chartjs-adapter-date-fns', href: 'https://github.com/chartjs/chartjs-adapter-date-fns', license: 'MIT', licenseHref: 'https://github.com/chartjs/chartjs-adapter-date-fns/blob/master/LICENSE.md' },
    ];
    let linksAttributionBackend = [
        { name: 'Ansible', href: 'https://www.ansible.com/', license: 'GPLv3', licenseHref: 'https://github.com/ansible/ansible/?tab=GPL-3.0-1-ov-file#readme' },
        { name: 'Ansible Runner', href: 'https://github.com/ansible/ansible-runner', license: 'Apache 2.0', licenseHref: 'https://github.com/ansible/ansible-runner/blob/devel/LICENSE.md' },
        { name: 'Django', href: 'https://www.djangoproject.com/', license: 'BSD 3-clause', licenseHref: 'https://opensource.org/license/bsd-3-clause' },
        { name: 'Django Rest Framework', href: 'https://www.django-rest-framework.org/', license: 'Custom', licenseHref: 'https://www.django-rest-framework.org/#license' },
        { name: 'Gunicorn', href: 'https://gunicorn.org/', license: 'MIT', licenseHref: 'https://github.com/benoitc/gunicorn/blob/master/LICENSE' },
        { name: 'pycryptodome', href: 'https://www.pycryptodome.org/', license: 'Public Domain / BSD', licenseHref: 'https://github.com/Legrandin/pycryptodome/blob/master/LICENSE.rst' },
        { name: 'pytz', href: 'https://pythonhosted.org/pytz/', license: 'MIT', licenseHref: 'https://github.com/stub42/pytz/blob/master/LICENSE.txt' },
        { name: 'pyyaml', href: 'https://pyyaml.org/', license: 'MIT', licenseHref: 'https://github.com/yaml/pyyaml/blob/main/LICENSE' },
        { name: 'grafana-django-saml2-auth', href: 'https://github.com/grafana/django-saml2-auth', license: 'MIT', licenseHref: 'https://github.com/grafana/django-saml2-auth/blob/main/LICENSE' },
        { name: 'djangorestframework-api-key', href: 'https://florimondmanca.github.io/djangorestframework-api-key/', license: 'MIT', licenseHref: 'https://github.com/florimondmanca/djangorestframework-api-key/blob/master/LICENSE' },
        { name: 'drf-spectacular', href: 'https://drf-spectacular.readthedocs.io/', license: 'BSD 3-Clause', licenseHref: 'https://github.com/tfranzel/drf-spectacular/blob/master/LICENSE' },
        { name: 'crontab', href: 'https://pypi.org/project/crontab/', license: 'LGPLv3', licenseHref: 'https://github.com/josiahcarlson/parse-crontab/blob/master/LICENSE3' },
        { name: 'premailer', href: 'https://premailer.io/', license: 'BSD 3-Clause', licenseHref: 'https://github.com/peterbe/premailer/blob/master/LICENSE' },
    ];
    let transitionParamsLeft = {
        x: -320,
        duration: 200,
        easing: sineIn
    };

    function t(code: string) : string {
      return tq($share, code);
    }
</script>
  
<Footer class="fixed bottom-0 start-0 w-full flex flex-wrap items-center justify-between pt-2 pb-1 pl-5 pr-5 border-t {classNavFooter}">
  <FooterCopyright by="OXL IT Services" href="https://github.com/O-X-L" copyrightMessage="" classA={classFooterText} />
  <FooterLinkGroup>
    <div class={classFooterText}>
      <a href="https://www.gnu.org/licenses/gpl-3.0.en.html" class={classFooterText}>{t('footer.oss.license')}: GPLv3</a> |
      <button class={classLinkHover} onclick={() => (hideAttributions = false)}>
        {t('footer.oss')}
      </button>
    </div>
  </FooterLinkGroup>
  <FooterLinkGroup class={classFooterText}>
    <div>
      {#if !$share.backend}
        <Spinner size="xs" />
      {:else}
        {#if $share.backend.authenticated}
        {t('footer.user')}: {$share.backend.user} |
        {/if}
        {t('footer.version')}: {$share.backend.version}
      {/if}
    </div>
  </FooterLinkGroup>
</Footer>

<Drawer backdrop={false} placement="left" transitionType="fly" id="drawer-attributions"
    transitionParams={transitionParamsLeft} bind:hidden={hideAttributions}
    class="bg-gray-800/85 dark:bg-gray-800/85" width="w-100">
    <div class="flex items-end">
        <CloseButton color="red" onclick={() => (hideAttributions = true)} class="mb-4" />
    </div>
    <div class="text-center text-xl font-bold mb-10">
        {t('footer.oss')}
    </div>
    <div>
        <div class="text-lg font-bold pb-6 max-sm:pt-6 max-sm:pb-2">{t('footer.oss.frontend')}:</div>
        <Listgroup active items={linksAttributionFrontend} let:item class="w-80">
            {item.name} | <a href={item.licenseHref}>{t('footer.oss.license')}: {item.license}</a>
        </Listgroup>    
    </div>
    <div>
        <div class="text-lg font-bold pb-6 max-sm:pt-6 max-sm:pb-2 mt-10">{t('footer.oss.backend')}:</div>
        <Listgroup active items={linksAttributionBackend} let:item class="w-80">
            {item.name} | <a href={item.licenseHref}>{t('footer.oss.license')}: {item.license}</a>
        </Listgroup>    
    </div>
</Drawer>