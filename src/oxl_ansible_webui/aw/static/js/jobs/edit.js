const CHOICE_SEPARATOR = ',';
const MULTI_CHOICE_FIELDS = ['id_inventory_file'];
const CHOICE_SELECTED_ATTR = 'aw-fs-choice-selected';
const CHOICE_SELECTED_FLAG = 'selected';
const CHOICES_CLASS_DIR = 'aw-fs-choice-dir';
const CHOICES_CLASS_FILE = 'aw-fs-choice-file';
const CHOICES_CLASS_VALUE = 'aw-fs-value';
const ELEM_ID_TMPL_PROMPT = 'aw-job-form-prompt-tmpl';
const ELEM_ID_PROMPTS = 'aw-job-form-prompts';
const ELEM_ID_PROMPT_PREFIX = 'aw-job-form-prompt-'
const API_FIELD_PROMPTS = 'execution_prompts';
const PROMPT_SIMPLE_TYPES = ['tags', 'skip_tags', 'mode_check', 'mode_diff', 'limit', 'env_vars', 'cmd_args', 'verbosity', 'credentials', 'limit_req', 'enforce'];
const PROMPT_SEPARATOR = ';';
const PROMPT_ARG_SEPARATOR = '#';
var PROMPT_ID = 0;

function apiBrowseDirFilteredChoices(choices, userInputCurrent, allowEmpty = false) {
    let choicesFiltered = [];
    for (choice of choices) {
        if (choice.startsWith(userInputCurrent)) {
            choicesFiltered.push(choice);
        }
    }
    choicesFiltered.sort();
    return choicesFiltered;
}

function fullUserInput(base, current) {
    let full;
    if (is_set(base)) {
        if (base.endsWith('/')) {
            full = base + current;
        } else {
            full = base + '/' +  current;
        }
    } else {
        full = current;
    }
    return full;
}

function apiBrowseDirUpdateChoices(inputElement, choicesElement, userInputCurrent, result, base) {
    let choices = result["files"];
    let inputElementId = $(inputElement).attr("id");
    let parentID = 'aw-fs-parent="' + inputElementId + '"'

    if (choices.length == 0) {
        inputElement.attr("title", "No available files/directories found.");
    } else if (choices[0] == '.*') {
        // isolated repository does not exist - cannot validate files
        return
    }

    let fileChoices = apiBrowseDirFilteredChoices(choices, userInputCurrent);
    let dirChoices = apiBrowseDirFilteredChoices(result['directories'], userInputCurrent);

    if (fileChoices.includes(userInputCurrent) || dirChoices.includes(userInputCurrent)) {
        hideChoices();
        return;
    }

    let choicesHtml = "";
    for ([i, choice] of fileChoices.entries()) {
        let choiceId = inputElementId + i;
        let choiceHtml = choice;
        if (is_set(userInputCurrent) && choice.startsWith(userInputCurrent)) {
            choiceHtml = "<b>" + userInputCurrent + "</b>" + choice.replace(userInputCurrent, '');
        }
        let fullChoice = fullUserInput(base, choice);
        choicesHtml += '<li id="' + choiceId + '" class="aw-fs-choice ' + CHOICES_CLASS_FILE + '"' + parentID + ' ' + CHOICES_CLASS_VALUE + '="' + fullChoice + '">' + choiceHtml + "</li>";
    }
    for ([i, dir] of dirChoices.entries()) {
        let choiceId = inputElementId + (i + fileChoices.length);
        let choiceHtml = dir;
        if (is_set(userInputCurrent) && dir.startsWith(userInputCurrent)) {
            choiceHtml = "<b>" + userInputCurrent + "</b>" + dir.replace(userInputCurrent, '');
        }
        let fullDir = fullUserInput(base, dir);
        if (!fullDir.endsWith('/')) {
            fullDir += '/';
        }
        choicesHtml += '<li id="' + choiceId + '" class="aw-fs-choice ' + CHOICES_CLASS_DIR + '" ' + parentID + ' ' + CHOICES_CLASS_VALUE + '="' + fullDir + '"><i class="fa fa-folder" aria-hidden="true"></i> ' + choiceHtml + "</li>";
    }
    choicesElement.innerHTML = choicesHtml;
    if ((fileChoices.length > 0 || dirChoices.length > 0) && !(fileChoices.includes(userInputCurrent) || dirChoices.includes(userInputCurrent))) {
        choicesElement.removeAttribute("hidden");
    }
}

function apiBrowseDirRemoveChoices(inputElement, choicesElement, exception) {
    console.log(exception);
    inputElement.attr("title", "You need to choose one of the existing files/directories");
}

function parseUserInput(userInput, inputElementId) {
    if (typeof(userInput) == 'undefined' || userInput == null) {
        userInput = "";
    }

    let userInputListLast = '';
    let userInputLevels = '';

    if (MULTI_CHOICE_FIELDS.includes(inputElementId)) {
        userInputListLast = userInput.split(CHOICE_SEPARATOR);
        userInputLevels = userInputListLast.pop().split('/');
    } else {
        if (userInput.includes(CHOICE_SEPARATOR)) {
            hideChoices();
            return;
        }
        userInputLevels = userInput.split('/');
    }
    let userInputCurrent = userInputLevels.pop();
    let base = userInputLevels.join('/');
    if (!is_set(userInputCurrent)) {
        cleanSelectedFlags(inputElementId);
    }
    return [base, userInputCurrent]
}

function apiBrowseDir(inputElement, choicesElement, repository) {
    if (!is_set(repository)){
        repository = '0';
    }

    let [base, userInputCurrent] = parseUserInput($(inputElement).val(), $(inputElement).attr("id"));

    $.ajax({
        url: "/api/fs/browse/" + repository + "?base=" + base,
        type: "GET",
        success: function (result) { apiBrowseDirUpdateChoices(inputElement, choicesElement, userInputCurrent, result, base); },
        error: function (exception) { apiBrowseDirRemoveChoices(inputElement, choicesElement, exception); },
    });
}

function getRepositoryToBrowse() {
    let selectedRepository = document.getElementById('id_repository').value;
    document.getElementById('id_playbook_file').setAttribute("aw-fs-repository", selectedRepository);
    document.getElementById('id_inventory_file').setAttribute("aw-fs-repository", selectedRepository);
}

function updateChoices($this) {
    let repository = $this.attr("aw-fs-repository");
    let apiChoices = document.getElementById($this.attr("aw-fs-choices"));

    apiBrowseDir($this, apiChoices, repository);
}

function hideChoices() {
    for (browseChoices of document.querySelectorAll('.aw-fs-choices')) {
        browseChoices.setAttribute("hidden", "hidden");
    }
}

function selectChoice(choiceElement) {
    let inputElement = document.getElementById(choiceElement.getAttribute("aw-fs-parent"));
    let value = choiceElement.getAttribute(CHOICES_CLASS_VALUE);
    let currentChoices = inputElement.value.split(CHOICE_SEPARATOR);
    currentChoices.pop();
    currentChoices = currentChoices.join(CHOICE_SEPARATOR);
    if (is_set(currentChoices)) {
        inputElement.value = currentChoices + CHOICE_SEPARATOR + value;
    } else {
        inputElement.value = value;
    }
    hideChoices();
}

function cleanSelectedFlags(choicesElementId) {
    let choicesList = document.getElementById(choicesElementId).getElementsByTagName("li");
    for (choice of choicesList) {
        if (is_set(choice.getAttribute(CHOICE_SELECTED_FLAG))) {
            choice.removeAttribute(CHOICE_SELECTED_FLAG);
        }
    }
}

function handleKeysUpDown($this, key_pressed) {
    // allow selection of choices using the up/down/enter keys
    let inputElementId = $this.attr("id");
    let choicesElementId = $this.attr("aw-fs-choices");
    let choicesElement = document.getElementById(choicesElementId);

    let selectedChoiceId = $this.attr(CHOICE_SELECTED_ATTR);
    let choicesList = choicesElement.getElementsByTagName("li");
    let maxChoiceId = choicesList.length - 1;
    let minChoiceId = 0;

    if (!is_set(selectedChoiceId)) {
        if (key_pressed == KEY_DOWN) {
            selectedChoiceId = minChoiceId;
        } else if (!is_set(selectedChoiceId)) {
            selectedChoiceId = maxChoiceId;
        }
    } else {
        selectedChoiceId = Number(selectedChoiceId);
        if (key_pressed == KEY_ENTER) {
            let selectedChoiceIdStr = inputElementId + selectedChoiceId;
            selectChoice(document.getElementById(selectedChoiceIdStr));
            updateChoices($this);

        } else if (key_pressed == KEY_DOWN) {
            if (selectedChoiceId >= maxChoiceId) {
                selectedChoiceId = minChoiceId;
            } else {
                selectedChoiceId += 1;
            }
        } else if (key_pressed == KEY_UP) {
             if (selectedChoiceId <= minChoiceId) {
                selectedChoiceId = maxChoiceId;
            } else {
                selectedChoiceId -= 1;
            }
        }
    }

    let selectedChoiceIdStr = inputElementId + selectedChoiceId;
    let selectedChoice = document.getElementById(selectedChoiceIdStr);
    if (is_set(selectedChoice)) {
        cleanSelectedFlags(choicesElementId);
        selectedChoice.setAttribute(CHOICE_SELECTED_FLAG, 1);
        $this.attr(CHOICE_SELECTED_ATTR, selectedChoiceId);
    }
}

function handleKeyTab($this) {
    // common auto-completion using the tab-key
    let choicesElement = document.getElementById($this.attr("aw-fs-choices"));
    let fileChoices = [];
    let fileChoicesElements = choicesElement.getElementsByClassName(CHOICES_CLASS_FILE);
    let dirChoices = [];
    let dirChoicesElements = choicesElement.getElementsByClassName(CHOICES_CLASS_DIR);

    if (is_set(dirChoicesElements)) {
        for (choice of dirChoicesElements) {
            dirChoices.push(choice.getAttribute(CHOICES_CLASS_VALUE));
        }
    }
    if (is_set(fileChoicesElements)) {
        for (choice of fileChoicesElements) {
            fileChoices.push(choice.getAttribute(CHOICES_CLASS_VALUE));
        }
    }

    if (fileChoices.length == 0 && dirChoices.length == 0) {
        return;
    }

    let match = undefined;
    let [userInputBase, userInputCurrent] = parseUserInput($this.val(), $this.attr("id"));

    for (file of fileChoices) {
        file = file.replace(userInputBase + '/', '')
        if (file.startsWith(userInputCurrent)) {
            if (is_set(match)) {
                return;
            }
            match = fullUserInput(userInputBase, file);
        }
    }

    if (!is_set(match)) {
        for (dir of dirChoices) {
            dir = dir.replace(userInputBase + '/', '')
            if (dir.startsWith(userInputCurrent)) {
                if (is_set(match)) {
                    return;
                }
                if (!dir.endsWith('/')) {
                    dir += '/';
                }
                match = fullUserInput(userInputBase, dir);
            }
        }
    }

    if (is_set(match)) {
        $this.val(match);
        updateChoices($this);
    }
}

function addPromptInputsWithDefaults(name, varName, kind, required, choices, regex) {
    PROMPT_ID += 1;
    let tmpl = document.getElementById(ELEM_ID_TMPL_PROMPT).innerHTML;
    tmpl = tmpl.replaceAll('${ID}', PROMPT_ID)
    let promptElement = document.createElement('div');
    promptElement.id = ELEM_ID_PROMPT_PREFIX + PROMPT_ID;

    if (!is_set(name)) {
        tmpl = tmpl.replaceAll('${NAME}', '');
    } else {
        tmpl = tmpl.replaceAll('${NAME}', name);
    }

    if (!is_set(varName)) {
        tmpl = tmpl.replaceAll('${VAR_NAME}', '');
    } else {
        tmpl = tmpl.replaceAll('${VAR_NAME}', varName);
    }

    if (kind == 'dropdown') {
        tmpl = tmpl.replaceAll('${kind_text}', '');
        tmpl = tmpl.replaceAll('${kind_dd}', 'selected');
    } else {
        tmpl = tmpl.replaceAll('${kind_text}', 'selected');
        tmpl = tmpl.replaceAll('${kind_dd}', '');
    }

    if (required == '1') {
        tmpl = tmpl.replaceAll('${req_req}', 'selected');
        tmpl = tmpl.replaceAll('${req_opt}', '');
    } else {
        tmpl = tmpl.replaceAll('${req_req}', '');
        tmpl = tmpl.replaceAll('${req_opt}', 'selected');
    }

    if (!is_set(regex)) {
       tmpl =  tmpl.replaceAll('${REGEX}', '');
    } else {
        tmpl = tmpl.replaceAll('${REGEX}', regex);
    }

    if (!is_set(choices)) {
        tmpl = tmpl.replaceAll('${CHOICES}', '');
    } else {
        tmpl = tmpl.replaceAll('${CHOICES}', choices);
    }

    promptElement.innerHTML = tmpl;
    document.getElementById(ELEM_ID_PROMPTS).append(promptElement);
}

function addPromptInputs() {
    addPromptInputsWithDefaults('', '', '', '', '', '');
}

function initPromptInputs() {
    if (PROMPT_CNF == 'None') {
        return;
    }
    for (let prompt of PROMPT_CNF.split(PROMPT_SEPARATOR)) {
        if (PROMPT_SIMPLE_TYPES.includes(prompt)) {
            continue;
        }
        let fields = prompt.split(PROMPT_ARG_SEPARATOR);
        let regex = fields[5];
        if (is_set(regex)) {
            regex = escapeQuotes(atob(regex));
        }

        addPromptInputsWithDefaults(fields[0], fields[1], fields[2], fields[3], fields[4], regex);
    }
}

function removePromptInputs(promptId) {
    document.getElementById(ELEM_ID_PROMPT_PREFIX + promptId).remove();
}

$( document ).ready(function() {
    getRepositoryToBrowse();
    setInterval('getRepositoryToBrowse()', (DATA_REFRESH_SEC * 500));
    initPromptInputs();

    $(".aw-main").on("submit", "#aw-job-form", function(event) {
        event.preventDefault();

        var form = $(this);
        var actionUrl = form.attr('action');
        var method = form.attr('method');
        var refresh = false;

        var job = [];
        var prompts = [];
        var promptFields = [];
        for (let field of form[0]) {
            if (['input', 'select'].includes(field.localName)) {
                if (field.name.startsWith('prompt_')) {
                    let fieldName = field.name.replaceAll('prompt_', '');
                    let promptNameParts = field.name.split('_');
                    if (PROMPT_SIMPLE_TYPES.includes(fieldName)) {
                        if (field.value == 'True') {
                            prompts.push(fieldName);
                        }
                        continue;
                    }

                    let promptId = promptNameParts[1];
                    fieldName = promptNameParts[2];
                    if (promptFields[promptId] === undefined) {
                        promptFields[promptId] = [];
                    }
                    promptFields[promptId][fieldName] = field.value;

                } else {
                    job.push(field.name + '=' + field.value);
                }
            }
        }

        for (let i = 1; i <= promptFields.length; i++) {
            if (promptFields[i] === undefined) {
                continue;
            }
            let prompt = [];
            prompt.push(promptFields[i].name);
            prompt.push(promptFields[i].varName);
            prompt.push(promptFields[i].kind);
            prompt.push(promptFields[i].required);
            prompt.push(promptFields[i].choices);
            prompt.push(btoa(escapeQuotes(promptFields[i].regex)));
            prompts.push(prompt.join(PROMPT_ARG_SEPARATOR));
        }

        job.push(API_FIELD_PROMPTS + '=' + prompts.join(PROMPT_SEPARATOR));

        var jobSerialized = job.join('&');

        $.ajax({
            type: method,
            url: actionUrl,
            data: jobSerialized,
            success: function (result) { apiActionSuccess(result); },
            error: function (result, exception) { apiActionError(result, exception); },
        });

        return false;
    });
    $(".aw-main").on("click", ".aw-job-form-prompt-add", function(){
        addPromptInputs();
    });
    $(".aw-main").on("click", ".aw-job-form-prompt-del", function(){
        removePromptInputs($(this).attr("name"));
    });
    $(".aw-main").on("input", ".aw-fs-browse", function(){
        updateChoices(jQuery(this));
    });
    $(".aw-main").on("click", ".aw-fs-choice", function(){
        selectChoice(document.getElementById($(this).attr("id")));
        updateChoices($(document.getElementById($(this).attr("aw-fs-parent"))));
    });
    $(".aw-main").on("focusin", ".row", function(){
        for (browseChoices of document.querySelectorAll('.aw-fs-choices')) {
            browseChoices.setAttribute("hidden", "hidden");
        }
    });
    $(".aw-main").on("focusin", ".aw-fs-browse", function(){
        updateChoices(jQuery(this));
    });
    $(".aw-main").on("click", ".aw-fs-browse", function(){
        updateChoices(jQuery(this));
    });
    $(".aw-main").on("keydown", ".aw-fs-browse", function(e){
        let key_pressed = e.which;
        if (![KEY_ENTER, KEY_TAB, KEY_UP, KEY_DOWN].includes(key_pressed)) {
            return;
        }
        e.preventDefault();
        if (key_pressed == KEY_TAB) {
            handleKeyTab(jQuery(this));
        } else {
            handleKeysUpDown(jQuery(this), key_pressed);
        }
    });
});
