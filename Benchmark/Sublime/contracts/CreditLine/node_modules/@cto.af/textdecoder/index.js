'use strict'

let TD = null
// Note: using globalThis is WAY more complicated than is needed.
if (typeof TextDecoder === 'function') {
  // This should be in most modern browsers, and node 11+
  TD = TextDecoder
} else if (typeof window !== 'undefined') {
  // eslint-disable-next-line no-undef
  TD = window.TextDecoder
} else if (typeof self !== 'undefined') {
  // eslint-disable-next-line no-undef
  TD = self.TextDecoder
} else {
  try {
    // Node 8.3 - 10
    const util = require('util')

    /* istanbul ignore next */
    if (typeof TD !== 'function') {
      // node 10
      TD = util.TextDecoder
    }
  } catch (ignored) {
    // util couldn't be loaded.  Probably an old browser.
  }
}

if (typeof TD !== 'function') {
  class TextDecoder {
    constructor(utfLabel, options) {
      this.utfLabel = utfLabel
      this.options = options
    }

    decode(buf) {
      // this isn't very good, but people should use more modern things
      // so they don't need it.
      const str = buf.toString(this.utfLabel)
      if (this.options.fatal) {
        for (const c of str) {
          // U+FFFD: REPLACEMENT CHARACTER
          if (c.codePointAt(0) === 0xFFFD) {
            const err = new TypeError(
              '[ERR_ENCODING_INVALID_ENCODED_DATA]: ' +
              'The encoded data was not valid for encoding ' + this.utfLabel
            )
            err.code = 'ERR_ENCODING_INVALID_ENCODED_DATA'
            err.errno = 12
            throw err
          }
        }
      }
      return str
    }
  }
  TD = TextDecoder
}
module.exports = TD
