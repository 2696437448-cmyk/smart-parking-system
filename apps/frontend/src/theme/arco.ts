export const arcoTheme = {
  primaryColor: "#37d7ff",
  borderRadius: "18px",
  dark: true,
  componentConfig: {
    Button: { shape: "round" as const },
    Card: { bordered: true },
    Form: { layout: "vertical" as const },
  },
};

export function createArcoTheme() {
  return arcoTheme;
}
