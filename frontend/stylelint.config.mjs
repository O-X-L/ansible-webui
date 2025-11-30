/** @type {import("stylelint").Config} */
// todo: also lint tailwind when a cli-tool becomes available: https://github.com/tailwindlabs/tailwindcss/discussions/5698
export default {
  "extends": ["stylelint-config-standard"],
  "rules": {
    "at-rule-no-unknown": [
      true,
      {
        "ignoreAtRules": [
          "source",
          "tailwind",
          "plugin",
          "custom-variant"
        ],
      },
    ],
  },
};
