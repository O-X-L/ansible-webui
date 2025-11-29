export interface formChoiceType {
  name: string,
  value: string|number|boolean,
}

export type inputColorType = 'base' | 'green' | 'red';

export interface formInfoType {
  defaults: any,
  choices: any,
}