'use strict';
const _ = require('lodash');
const _Decimal = require('decimal.js-light');

const PRECISION = 120;

// 300 digits of E
const E =
'2.718281828459045235360287471352662497757247093699959574966967627724076630' +
'35354759457138217852516642742746639193200305992181741359662904357290033429' +
'52605956307381323286279434907632338298807531952510190115738341879307021540' +
'89149934884167509244761460668082264800168477411853742345442437107539077744' +
'99207';

// 300 digits of LN10
const LN10 =
'2.302585092994045684017991454684364207601101488628772976033327900967572609' +
'67735248023599720508959829834196778404228624863340952546508280675666628736' +
'90987816894829072083255546808437998948262331985283935053089653777326288461' +
'63366222287698219886746543667474404243274365155048934314939391479619404400' +
'22211';

// 300 Digits of PI
const PI =
'3.141592653589793238462643383279502884197169399375105820974944592307816406' +
'28620899862803482534211706798214808651328230664709384460955058223172535940' +
'81284811174502841027019385211055596446229489549303819644288109756659334461' +
'28475648233786783165271201909145648566923460348610454326648213393607260249' +
'14127';


const Decimal = _Decimal.clone({precision: 120, LN10: LN10});
const HEX_REGEX = /^0x[0-9a-f]*$/i;
const BIN_REGEX = /^0b[01]*$/i;
const OCTAL_REGEX = /^0[0-9]*$/;
const HEX_DIGITS =
	['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'];
const HEX_DIGIT_VALUES =
	_.zipObject(HEX_DIGITS, _.times(HEX_DIGITS.length));
const OCTAL_DIGITS =
	['0','1','2','3','4','5','6','7'];
const OCTAL_DIGIT_VALUES =
	_.zipObject(OCTAL_DIGITS, _.times(OCTAL_DIGITS.length));
const BIN_DIGITS =
	['0','1'];
const BIN_DIGIT_VALUES =
	_.zipObject(BIN_DIGITS, _.times(BIN_DIGITS.length));


function _toInt(d) {
	return d.todp(0, _Decimal.ROUND_DOWN);
}

class ParseError extends Error {
	constructor(msg) {
		super(msg);
	}
}

function toDecimal(v) {
	if (v instanceof Decimal)
		return v;
	if (_.isNaN(v))
		throw new ParseError('NaN is not a valid number.');
	v = v || 0;
	if (typeof(v) == 'string') {
		// Catch hex encoding.
		if (v.match(HEX_REGEX))
			return baseDecode(v.substr(2).toLowerCase(), HEX_DIGIT_VALUES);
		// Catch binary encoding.
		else if (v.match(BIN_REGEX))
			return baseDecode(v.substr(2), BIN_DIGIT_VALUES);
		// Catch octal encoding.
		else if (v.match(OCTAL_REGEX))
			return baseDecode(v.substr(1), OCTAL_DIGIT_VALUES);
	}
	else if (_.isBuffer(v)) {
		return baseDecode(v.toString('hex').toLowerCase(), HEX_DIGIT_VALUES);
	} else if (typeof(v) == 'boolean')
		v = v ? 1 : 0;
	try {
		return new Decimal(v);
	} catch (err) {
		throw new ParseError(`Cannot parse "${v}" as a number`);
	}
}

function baseDecode(s, digitValues) {
	s = s || digitValues[0];
	const base = _.keys(digitValues).length;
	const values = _.map(s, ch => digitValues[ch]);
	let r = new Decimal(0);
	for (let v of values)
		r = r.mul(base).add(v);
	return r;
}

function toOctal(v, length=null) {
	return '0' + baseEncode(toDecimal(v), OCTAL_DIGITS, length);
}

function toHex(v, length=null) {
	return '0x' + baseEncode(toDecimal(v), HEX_DIGITS, length);
}

function toBinary(v, length=null) {
	return '0b' + baseEncode(toDecimal(v), BIN_DIGITS, length);
}

function baseEncode(d, digits, length=null) {
	const base = digits.length;
	if (d.dp() > 0 || d.lt(0))
		throw new Error('Can only base-${base} encode positive integers');
	length = length || 0;
	const L = Math.abs(length);
	let r = '';
	do {
		r = digits[d.mod(base)] + r;
		d = _toInt(d.div(base));
	} while (d.gt(0)) ;
	if (L) {
		if (r.length < L) {
			// Pad.
			const padding = _.repeat(digits[0], L - r.length);
			if (length > 0)
				r = padding + r;
			else
				r = r + padding;
		} else if (r.length > L) {
			// Truncate.
			if (length > 0)
				r = r.substr(r.length - L);
			else
				r = r.substr(0, L);
		}
	}
	return r;
}

function toBits(d, length=null) {
	d = toDecimal(d);
	if (d.dp() > 0 || d.lt(0))
		throw new Error('Can only bit encode positive integers');
	length = length || 0;
	const L = Math.abs(length);
	// Construct bits in reverse.
	let bits = [];
	do {
		bits.push(_toInt(d.mod(2)).toNumber());
		d = _toInt(d.div(2));
	} while (d.gt(0)) ;
	bits = _.reverse(bits);
	if (L) {
		if (bits.length < L) {
			// Pad.
			const padding = _.times(L - bits.length, i => 0);
			if (length > 0)
				bits = [...padding, ...bits];
			else
				bits = [...bits, ...padding];
		} else if (bits.length > L) {
			// Truncate.
			if (length > 0)
				bits = bits.slice(bits.length - L);
			else
				bits = bits.slice(0, L);
		}
	}
	return bits;
}

function fromBits(bits) {
	return expand('0b' + bits.join(''));
}

function expand(v) {
	return toDecimal(v).toFixed();
}

function add(a, b) {
	return toDecimal(a).plus(toDecimal(b)).toFixed();
}

function sub(a, b) {
	return toDecimal(a).minus(toDecimal(b)).toFixed();
}

function mul(a, b) {
	return toDecimal(a).times(toDecimal(b)).toFixed();
}

function div(a, b) {
	return toDecimal(a).div(toDecimal(b)).toFixed();
}

function mod(a, b) {
	return toDecimal(a).mod(toDecimal(b)).toFixed();
}

function eq(a, b) {
	return toDecimal(a).eq(toDecimal(b));
}

function ne(a, b) {
	return !eq(a, b);
}

function gt(a, b) {
	return toDecimal(a).gt(toDecimal(b));
}

function gte(a, b) {
	return toDecimal(a).gte(toDecimal(b));
}

function lt(a, b) {
	return toDecimal(a).lt(toDecimal(b));
}

function lte(a, b) {
	return toDecimal(a).lte(toDecimal(b));
}

function max(a,b) {
	a = toDecimal(a);
	b = toDecimal(b);
	if (a.gt(b))
		return a.toFixed();
	return b.toFixed();
}

function min(a,b) {
	a = toDecimal(a);
	b = toDecimal(b);
	if (a.lt(b))
		return a.toFixed();
	return b.toFixed();
}

function clamp(x, lo, hi) {
	x = toDecimal(x);
	lo = toDecimal(lo);
	hi = toDecimal(hi);
	if (lo.gt(hi)) {
		const t = lo;
		lo = hi;
		hi = t;
	}
	if (x.lt(lo))
		return lo.toFixed();
	if (x.gt(hi))
		return hi.toFixed();
	return x.toFixed();
}

function int(a) {
	return _toInt(toDecimal(a)).toFixed();
}

function round(a) {
	return toDecimal(a).todp(0, _Decimal.ROUND_HALF_UP).toFixed();
}

function abs(a) {
	return toDecimal(a).abs().toFixed();
}

function idiv(a, b) {
	return _toInt(toDecimal(a).div(toDecimal(b))).toFixed();
}

function sum(...vals) {
	let r = new Decimal(0);
	vals = _.flatten(vals);
	for (let v of vals)
		r = r.add(toDecimal(v));
	return r.toFixed();
}

function neg(v) {
	return toDecimal(v).neg().toFixed();
}

function cmp(a, b) {
	a = toDecimal(a);
	b = toDecimal(b);
	if (a.lt(b))
		return -1;
	if (a.gt(b))
		return 1;
	return 0;
}

function pow(x, y) {
	x = toDecimal(x);
	y = toDecimal(y);
	return x.pow(y).toFixed();
}

function exp(y) {
	return pow(E, y);
}

function log(x, base) {
	x = toDecimal(x);
	if (_.isNil(base))
		base = toDecimal(E);
	return x.log(base).toFixed();
}

function toBuffer(v, size) {
	let hex = toHex(v, size ? size*2 : null).substr(2);
	if (hex.length % 2) {
		if (size < 0)
			hex = hex + '0';
		else
			hex = '0' + hex;
	}
	return Buffer.from(hex, 'hex');
}

function toNumber(v) {
	return toDecimal(v).toNumber();
}

function split(v) {
	v = expand(v);
	const m = /^([-+])?(\d+)(\.(\d+))?$/.exec(v);
	return {
		sign: m[1] || '',
		integer: m[2],
		decimal: m[4] || ''
	};
}

function sd(v, n=null) {
	v = toDecimal(v);
	if (!_.isNumber(n))
		return v.sd().toFixed();
	return v.tosd(n).toFixed();
}

function dp(v, n=null) {
	v = toDecimal(v);
	if (!_.isNumber(n))
		return v.dp();
	return v.todp(n).toFixed();
}

function sign(v) {
	v = toDecimal(v);
	if (v.gte(0))
		return 1;
	return -1;
}

module.exports = {
	expand: expand,
	parse: expand,
	add: add,
	plus: add,
	sub: sub,
	minus: sub,
	mul: mul,
	times: mul,
	div: div,
	over: div,
	mod: mod,
	eq: eq,
	ne: ne,
	gt: gt,
	lt: lt,
	gte: gte,
	lte: lte,
	max: max,
	min: min,
	clamp: clamp,
	int: int,
	round: round,
	idiv: idiv,
	sum: sum,
	neg: neg,
	negate: neg,
	cmp: cmp,
	abs: abs,
	pow: pow,
	exp, exp,
	sqrt: (x) => pow(x, 0.5),
	log: log,
	ln: (x) => log(x),
	raise: pow,
	split: split,
	sign: sign,
	dp: dp,
	sd: sd,
	toHex: toHex,
	toHexadecimal: toHex,
	toBinary: toBinary,
	toOctal: toOctal,
	toBuffer: toBuffer,
	toNumber: toNumber,
	toBits: toBits,
	fromBits: fromBits,
	E: E.substr(0, 1+PRECISION),
	LN10: LN10.substr(0, 1+PRECISION),
	PI: PI.substr(0, 1+PRECISION),
	ParseError: ParseError
};
