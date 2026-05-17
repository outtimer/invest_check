import { test, expect } from '@playwright/test';

test('API de preço retorna JSON válido para PETR4', async ({ request }) => {
  const response = await request.get('/api/preco/PETR4');
  expect(response.ok()).toBeTruthy();

  const body = await response.json();
  expect(body).toHaveProperty('preco');
  expect(typeof body.preco).toBe('number');
});

test('Modal de nova operação abre corretamente em watchlist', async ({ page }) => {
  await page.goto('/watchlist');
  await page.getByRole('button', { name: /NOVA OPERAÇÃO/i }).click();
  await expect(page.getByText('Registrar Operação')).toBeVisible();
  await expect(page.getByPlaceholder('PETR4')).toBeVisible();
  await expect(page.getByRole('button', { name: /SALVAR OPERAÇÃO/i })).toBeVisible();
});
