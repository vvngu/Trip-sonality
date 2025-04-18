module.exports = {
  plugins: [
    // 使用 @tailwindcss/postcss 插件（它会正确调用 tailwindcss 主包）
    require("@tailwindcss/postcss")({
      config: "./tailwind.config.cjs",
    }),
    require("autoprefixer"),
  ],
};
