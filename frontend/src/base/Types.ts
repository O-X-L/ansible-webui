export interface formChoiceType {
  name: string,
  value: string|number,
}

export interface formAlertType {
  color: string,
  title: string,
  msg: string,
}

export type inputColorType = 'base' | 'green' | 'red';

export interface formInfoType {
  defaults: any,
  choices: any,
}