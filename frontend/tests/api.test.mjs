import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';

const { apiRequest, ApiError } = await import(
  new URL('api/client.js', process.env.API_TEST_BUILD_URL)
);
const { login, getCurrentUser } = await import(
  new URL('api/auth.js', process.env.API_TEST_BUILD_URL)
);
const originalFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = originalFetch; });

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), { status });
}

test('login sends encoded credentials to the relative endpoint and returns token', async () => {
  const credentials = { email: 'test+tag@example.com', password: 'synthetic &+=?#% password' };
  const token = { access_token: 'synthetic-token', token_type: 'bearer' };
  globalThis.fetch = async (path, options) => {
    assert.equal(path, '/auth/login');
    assert.equal(options.method, 'POST');
    assert.equal(options.headers.get('Content-Type'), 'application/x-www-form-urlencoded');
    assert.equal(options.headers.get('Accept'), 'application/json');
    assert.ok(options.body instanceof URLSearchParams);
    const encoded = options.body.toString();
    assert.match(encoded, /%2B/);
    assert.match(encoded, /%26/);
    const decoded = new URLSearchParams(encoded);
    assert.deepEqual([...decoded], [['username', credentials.email], ['password', credentials.password]]);
    return jsonResponse(token);
  };
  assert.deepEqual(await login(credentials), token);
});

test('getCurrentUser sends bearer token without body and returns user', async () => {
  const user = { email: 'test@example.com', full_name: 'Test User', id: 42 };
  globalThis.fetch = async (path, options) => {
    assert.equal(path, '/auth/me');
    assert.equal(options.method, 'GET');
    assert.equal(options.headers.get('Authorization'), 'Bearer synthetic-token');
    assert.equal(options.headers.get('Accept'), 'application/json');
    assert.equal(options.headers.has('Content-Type'), false);
    assert.equal(options.body, undefined);
    return jsonResponse(user);
  };
  assert.deepEqual(await getCurrentUser('synthetic-token'), user);
});

test('client preserves caller headers including an explicit Accept header', async () => {
  globalThis.fetch = async (_path, options) => {
    assert.equal(options.headers.get('Accept'), 'application/custom+json');
    assert.equal(options.headers.get('X-Test'), 'example');
    assert.equal(options.headers.has('Content-Type'), false);
    return jsonResponse({});
  };
  await apiRequest('/example', { headers: new Headers({ Accept: 'application/custom+json', 'X-Test': 'example' }) });
});

for (const [status, kind] of [[401, 'authentication'], [403, 'forbidden'], [422, 'validation'], [500, 'server'], [404, 'http']]) {
  test(`HTTP ${status} is classified as ${kind} and preserves detail`, async () => {
    const detail = status === 422
      ? [{ loc: ['body', 'username'], msg: 'Field required', type: 'missing' }]
      : 'Synthetic error detail';
    globalThis.fetch = async () => jsonResponse({ detail }, status);
    await assert.rejects(apiRequest('/example'), (error) => {
      assert.ok(error instanceof ApiError);
      assert.equal(error.kind, kind);
      assert.equal(error.status, status);
      assert.deepEqual(error.detail, detail);
      return true;
    });
  });
}

for (const [status, kind] of [[401, 'authentication'], [500, 'server']]) {
  test(`non-JSON HTTP ${status} retains classification`, async () => {
    globalThis.fetch = async () => new Response('<html>Error</html>', { status });
    await assert.rejects(apiRequest('/example'), (error) => {
      assert.ok(error instanceof ApiError);
      assert.equal(error.kind, kind);
      assert.equal(error.status, status);
      assert.equal(error.detail, undefined);
      return true;
    });
  });
}

test('rejected fetch becomes a network error without leaking its message', async () => {
  globalThis.fetch = async () => { throw new TypeError('synthetic-private-token'); };
  await assert.rejects(apiRequest('/example'), (error) => {
    assert.ok(error instanceof ApiError);
    assert.equal(error.kind, 'network');
    assert.equal(error.status, null);
    assert.equal(error.detail, undefined);
    assert.equal(error.message.includes('synthetic-private-token'), false);
    return true;
  });
});

test('malformed successful JSON becomes a response error', async () => {
  globalThis.fetch = async () => new Response('not JSON', { status: 200 });
  await assert.rejects(apiRequest('/example'), (error) => {
    assert.ok(error instanceof ApiError);
    assert.equal(error.kind, 'response');
    assert.equal(error.status, 200);
    return true;
  });
});

test('HTTP error messages do not reflect sensitive response details', async () => {
  globalThis.fetch = async () => jsonResponse({ detail: 'synthetic-private-password' }, 401);
  await assert.rejects(apiRequest('/example'), (error) => {
    assert.equal(error.message.includes('synthetic-private-password'), false);
    return true;
  });
});
