![build status](https://travis-ci.org/merklejerk/bn-str-256.svg?branch=master)
[![npm package](https://badge.fury.io/js/bn-str-256.svg)](https://www.npmjs.com/package/bn-str-256)

# **bn-str-256**
A simple, functional library for big number math,
with up to 120 digits of precision, more than suitable for working with 256-bit/32-byte numbers used in domains like blockchain.

What sets this apart from other big number libraries is a very simple
functional syntax where most operations result in a **decimal
string** (e.g., `'412.959'`), which, depending on
your application, may be a more useful representation.

Additionally, all functions accept plain numbers, decimal strings, exponential
strings (e.g., `'1.5e-8'`), hex (e.g., `'0xf00b47'`),
binary (e.g., `'0b10011'`), or octal (e.g., `'04471'`) encodings,
as well as node `Buffer` objects as input. The library can likewise convert
numbers to any of these encodings or `Buffer` objects.

This library is built as a wrapper around the awesome [decimal.js-light](https://github.com/MikeMcl/decimal.js-light) library.

### Installation
```bash
npm install bn-str-256
# or
yarn add bn-str-256
```

### Examples
```js
const bn = require('bn-str-256');

// Add two numbers.
bn.add(1234, '0x4953'); // '20005'
// Subtract two numbers.
bn.sub(1234, '1.5e-3'); // '1233.9985''
// Multiply two numbers.
bn.mul('1234.521', '305'); // output '376528.905'
// Divide two numbers.
bn.div(1234, '0x4953'); // '0.06573970486...'
// Take the modulo of two numbers.
bn.mod('1.412e8', 33); // '29'
// Raise to a power.
bn.pow(1234, 8); // '5376767751082385640407296'
// Take the 3rd root.
bn.pow(1234, 1/3); // '10.7260146688...'
// Remove decimals.
bn.int(44.4121); // '44'
// Round.
bn.round(44.68); // '45'
// Count decimal places.
bn.dp(44.312); // 3
// Count significant digits.
bn.dp(44.312); // 5
// Truncate decimal places.
bn.dp(44.312, 2); // '44.31'
// Truncate significant digits.
bn.dp(44.312, 3); // '44.3'
// Get the sign of a number.
bn.sign('-31.4121'); // -1
// Work with some big numbers
bn.sub('0x8ffffffffffffffffffffffffffffffffffffff',
 '1591029491249109201931039109512131121212') // '51380915346385064...'

// Compare numbers a variety of ways.
bn.cmp(1, 2); // -1
bn.gt(321, 321); // false
bn.gte(321, 321); // true
bn.lt(320, 321); // true
bn.lte(320, 321); // true

// Take the minimum of two values.
bn.min('1294.31221944', '5.421e6'); // '1294.31221944'
// Take the maximum of two values.
bn.min('1294.31221944', '5.421e6'); // '5421000'
// Clamp a value to within an interval.
bn.min('1600', '1294.31221944', '5.421e6'); // '1600'

// Just parse a hex value.
bn.parse('0x49121') // '299297'
// Just parse a binary value.
bn.parse('0b1001') // '9'
// Just parse a Buffer object.
bn.parse(Buffer.from('foo')); // 6713199

// Do some math and output a hex string.
bn.toHex(bn.mul('3043131212', '495')); // 0x15eb97423f4
// Left pad a hex string to 20 digits.
bn.toHex('4491959969129121', 20); // 0x0000000ff569ee4e22a1
// Convert to a buffer.
bn.toBuffer('99129129412'); // <Buffer 17 14 8e 79 c4>
// Convert to native javascript Number type.
bn.toNumber('0x491fc712d'); // 19629109549

// Split a number up into its parts.
bn.split('-34.99'); // { sign: '-', integer: '34', decimal: '99' }

```

### All Functions
| name (*alias*) | description |
|----------------|-------------|
| `parse(x)` (*expand*) | convert a Number, exponential string, hex/octal/binary-encoded string, or buffer object into a decimal string |
| `add(a, b)` (*plus*) | Add `a` and `b` |
| `sub(a, b)` (*minus*) | Subtract `b` from `a` |
| `mul(a, b)` (*times*) | Multiply `a` and `b` |
| `div(a, b)` (*over*) | Divide `a` over `b` |
| `idiv(a, b)` | Divide `a` by `b` and return the integer portion |
| `mod(a, b)` | `a` modulo `b` |
| `pow(x, y)` (*raise*) | Raise `x` to the `y` power |
| `log(x)` (*ln*) | Natural logarithm of `x` |
| `log(x, base)` | Logarithm of `x` with base `y` |
| `int(x)` | Return the integer portion of `x` (no rounding) |
| `round(x)` | Round `x` to an integer |
| `sum(...args)` | Sum all arguments |
| `neg(x)` (*negate*) | Negate `x` |
| `abs(x)` | Take the absolute value of `x` |
| `sqrt(x)` | Take the square root of `x` |
| `exp(y)` | Raise the mathematical constant *e* to `y` |
| `max(a, b)` | Take the maximum of `a` and `b` |
| `min(a, b)` | Take the minimum of `a` and `b` |
| `clamp(x, l, h)` | Clamp `x` to be within `l` and `h`, inclusive |
| `sd(x)` | Get the number of significant digits of `x` |
| `sd(x, n)` | Set the number of significant digits of `x` to `n` |
| `dp(x)` | Get the number of decimal places of `x` |
| `dp(x, n)` | Set the number of decimal places of `x` to `n` |
| `sign(x)` | Get the sign of `x` (`-1` if `x < 0`, `1` otherwise) |
| `cmp(a, b)` | Compare `a` with `b`(where `-1` if `a < b`, `0` if `a == b`, `1` if a > b) |
| `eq(a, b)` | Test if `a == b` |
| `ne(a, b)` | Test if `a != b` |
| `gt(a, b)` | Test if `a > b` |
| `lt(a, b)` | Test if `a < b` |
| `gte(a, b)` | Test if `a >= b` |
| `lte(a, b)` | Test if `a <= b` |
| `toHex(x)` | Convert `x` to a hex string (e.g., `0xf3abb`) |
| `toHex(x, length)` | Convert `x` to a hex string and left truncate/pad it to `length` digits. If `length` is negative, the result will be right padded/truncated. |
| `toOctal(x)` | Convert `x` to an octal string (e.g., `04335`) |
| `toOctal(x, length)` | Convert `x` to an octal string and left truncate/pad it to `length` digits. If `length` is negative, the result will be right padded/truncated. |
| `toBinary(x)` | Convert `x` to a binary string (e.g., `0b10111010`)|
| `toBinary(x, length)` | Convert `x` to a binary string and left truncate/pad it to `length` digits. If `length` is negative, the result will be right padded/truncated.  |
| `toBuffer(x)` | Convert `x` to a `Buffer` object |
| `toBuffer(x, size)` | Convert `x` to a `Buffer` object, and left truncate/pad it to `size` bytes. If `size` is negative, the result will be right padded/truncated. |
| `toBits(x)` | Convert `x` to an array of `1`s and `0`s representing its bits. |
| `toBits(x, length)` | Convert `x` to bit array and left truncate/pad it to `length` digits. If `length` is negative, the result will be right padded/truncated. |
| `fromBits(bits)` | Convert a `bits` array of `1`s and `0`s to a number |
| `toNumber(x)` | Convert `x` to a native `Number` type. Precision loss may occur. |
| `E` | The mathematical constant *e* (`2.71828...`) |
| `PI` | The mathematical constant *π* (`3.1415926...`) |
