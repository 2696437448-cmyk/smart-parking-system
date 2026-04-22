export const arcoTheme = {
  primaryColor: "#2f6fed",
  borderRadius: "16px",
  dark: false,
  componentConfig: {
    Button: { shape: "round" as const },
    Card: { bordered: true },
    Form: { layout: "vertical" as const },
  },
};

function applyArcoTheme() {
  if (typeof document === "undefined") {
    return;
  }
  document.body.setAttribute("arco-theme", arcoTheme.dark ? "dark" : "light");
  document.documentElement.style.setProperty("--tech-arco-primary", arcoTheme.primaryColor);
  document.documentElement.style.setProperty("--tech-arco-radius", arcoTheme.borderRadius);
}

type ArcoComponentOptions = {
  classPrefix?: string;
  componentPrefix?: string;
};

export function createArcoTheme(): ArcoComponentOptions {
  applyArcoTheme();
  return {};
}
