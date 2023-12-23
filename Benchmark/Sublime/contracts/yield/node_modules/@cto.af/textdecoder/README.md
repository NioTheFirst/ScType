# Simple TextDecoder polyfill

I needed this in two different projects, so I pulled it out.  All of the existing TextDecoder polyfills try to do too much for what I needed.

This just finds the best TextDecoder instance it can, and mocks in a dirty one for really old environments.

## Use

```js
const TextDecoder = require('@cto.af/textdecoder')
```
