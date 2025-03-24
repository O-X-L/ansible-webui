<script lang="ts">
    let { title } = $props();

    const CSP_HASHES = [
        'sha256-cQ9xCH3WIkOcdnghiinxGOIpzxIYR6hPc6TY3BcTRXc=',  // translate
    ];  // NOTE: have also to be added to src/oxl_ansible_webui/aw/templates/base.html
</script>

<title>{title}</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="robots" content="noindex, nofollow">
<meta name="color-scheme" content="light dark" />
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src * data:; style-src 'self' 'unsafe-inline'; script-src-elem 'self' '{CSP_HASHES[0]}'">
<link href="/static/css/global.css" rel="stylesheet" type="text/css" crossorigin="anonymous" referrerpolicy="no-referrer">
<link href="/static/dist/tailwind.min.css" rel="stylesheet" type="text/css" crossorigin="anonymous" referrerpolicy="no-referrer">
