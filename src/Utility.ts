export class ObjectSet<T extends object> {
	private _set: Set<string>;
	constructor() {
		this._set = new Set();
	}

	public add(value: T): this {
		this._set.add(JSON.stringify(value));
		return this;
	}

	public has(value: T): boolean {
		return this._set.has(JSON.stringify(value));
	}

	public forEach(callback: (value: T, index: number, array: T[]) => void) {
		const parsed: T[] = Array.from(this._set).map((x) => JSON.parse(x));
		parsed.forEach(callback);
	}
}

export class ObjectMap<K extends object, V> {
	private _map: Map<string, V>;
	constructor() {
		this._map = new Map<string, V>();
	}

	public GetPrimitive(): Map<string, V> {
		return this._map;
	}

	public has(key: K): boolean {
		return this._map.has(JSON.stringify(key));
	}

	public get(key: K): V | undefined {
		return this._map.get(JSON.stringify(key));
	}

	public set(key: K, value: V): this {
		this._map.set(JSON.stringify(key), value);
		return this;
	}

	public forEach(callback: (value: V, key: K, map: Map<K, V>) => void) {
		const parsed = new Map(Array.from(this._map.entries()).map(([key, value]) => [JSON.parse(key), value]));
		parsed.forEach(callback);
	}
}
