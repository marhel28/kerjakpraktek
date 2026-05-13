export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();

  try {
    const data = await $fetch(`${config.public.apiBase}/abouts`);
    return data;
  } catch (err: any) {
    console.error("About fetch error:", err);
    return null;
  }
});