export interface formChoiceType {
  name: string,
  value: string|number|boolean,
};

export type inputColorType = 'base' | 'green' | 'red';

export interface formInfoType {
  defaults: any,
  choices: any,
};

export type entryActionState = {
    clone: boolean;
    edit: boolean;
};

export type entryActionStateExec = {
    clone: boolean;
    edit: boolean;
    exec: boolean;
};
