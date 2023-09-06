/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software Project course.
 * � Copyright Utrecht University (Department of Information and Computing Sciences)
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

export enum ErrorCode {
	OK,
	HANDLED_ERRNO,
	NO_INTERNET_CONN,
	SRCML_NOT_INSTALLED,
}

export default class Error {
	public static Code: ErrorCode = ErrorCode.OK;
	
}
