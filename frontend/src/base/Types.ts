export interface formChoice {
  name: string,
  value: string,
}

export interface formAlerts {
  color: string,
  title: string,
  msg: string,
}

export type inputColor = 'base' | 'green' | 'red';

export interface formInfoType {
  defaults: any,
  choices: any,
}