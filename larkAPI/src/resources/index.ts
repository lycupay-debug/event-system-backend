import type * as lark from "@larksuiteoapi/node-sdk";
import { normalizeLarkApiError } from "../errors";

type SdkMethod = (...args: any[]) => Promise<unknown>;
type PayloadOf<T extends SdkMethod> = NonNullable<Parameters<T>[0]>;

/**
 * Preserve the official SDK request and response types while keeping its
 * internal request-options type out of this library's public method signatures.
 */
function safe<T extends SdkMethod>(
  operation: string,
  owner: unknown,
  method: T,
): (payload: PayloadOf<T>) => Promise<Awaited<ReturnType<T>>> {
  const wrapped = async (payload: PayloadOf<T>) => {
    try {
      return await method.call(owner, payload);
    } catch (error) {
      throw normalizeLarkApiError(error, operation);
    }
  };

  return wrapped as (
    payload: PayloadOf<T>
  ) => Promise<Awaited<ReturnType<T>>>;
}

/**
 * Named, grouped Bitable API methods exposed by the official SDK generated
 * client. Request and response types are inferred from the pinned SDK declarations.
 * API_COVERAGE.md tracks endpoint inventory and verification state.
 */
export function createBitableMethods(client: lark.Client) {
  const b = client.bitable;

  return {
    apps: {
      create: safe("bitable.app.create", b.app, b.app.create),
      get: safe("bitable.app.get", b.app, b.app.get),
      update: safe("bitable.app.update", b.app, b.app.update),
      copy: safe("bitable.app.copy", b.app, b.app.copy),
    },
    tables: {
      create: safe("bitable.appTable.create", b.appTable, b.appTable.create),
      list: safe("bitable.appTable.list", b.appTable, b.appTable.list),
      update: safe("bitable.appTable.patch", b.appTable, b.appTable.patch),
      delete: safe("bitable.appTable.delete", b.appTable, b.appTable.delete),
      batchCreate: safe("bitable.appTable.batchCreate", b.appTable, b.appTable.batchCreate),
      batchDelete: safe("bitable.appTable.batchDelete", b.appTable, b.appTable.batchDelete),
    },
    records: {
      create: safe("bitable.appTableRecord.create", b.appTableRecord, b.appTableRecord.create),
      get: safe("bitable.appTableRecord.get", b.appTableRecord, b.appTableRecord.get),
      list: safe("bitable.appTableRecord.list", b.appTableRecord, b.appTableRecord.list),
      search: safe("bitable.appTableRecord.search", b.appTableRecord, b.appTableRecord.search),
      update: safe("bitable.appTableRecord.update", b.appTableRecord, b.appTableRecord.update),
      delete: safe("bitable.appTableRecord.delete", b.appTableRecord, b.appTableRecord.delete),
      batchCreate: safe("bitable.appTableRecord.batchCreate", b.appTableRecord, b.appTableRecord.batchCreate),
      batchGet: safe("bitable.appTableRecord.batchGet", b.appTableRecord, b.appTableRecord.batchGet),
      batchUpdate: safe("bitable.appTableRecord.batchUpdate", b.appTableRecord, b.appTableRecord.batchUpdate),
      batchDelete: safe("bitable.appTableRecord.batchDelete", b.appTableRecord, b.appTableRecord.batchDelete),
    },
    fields: {
      create: safe("bitable.appTableField.create", b.appTableField, b.appTableField.create),
      list: safe("bitable.appTableField.list", b.appTableField, b.appTableField.list),
      update: safe("bitable.appTableField.update", b.appTableField, b.appTableField.update),
      delete: safe("bitable.appTableField.delete", b.appTableField, b.appTableField.delete),
    },
    views: {
      create: safe("bitable.appTableView.create", b.appTableView, b.appTableView.create),
      get: safe("bitable.appTableView.get", b.appTableView, b.appTableView.get),
      list: safe("bitable.appTableView.list", b.appTableView, b.appTableView.list),
      update: safe("bitable.appTableView.patch", b.appTableView, b.appTableView.patch),
      delete: safe("bitable.appTableView.delete", b.appTableView, b.appTableView.delete),
    },
    forms: {
      get: safe("bitable.appTableForm.get", b.appTableForm, b.appTableForm.get),
      update: safe("bitable.appTableForm.patch", b.appTableForm, b.appTableForm.patch),
      upgrade: safe("bitable.appTableForm.upgrade", b.appTableForm, b.appTableForm.upgrade),
      listFields: safe("bitable.appTableFormField.list", b.appTableFormField, b.appTableFormField.list),
      updateField: safe("bitable.appTableFormField.patch", b.appTableFormField, b.appTableFormField.patch),
    },
    fieldGroups: {
      create: safe("bitable.appTableFieldGroup.create", b.appTableFieldGroup, b.appTableFieldGroup.create),
    },
    dashboards: {
      list: safe("bitable.appDashboard.list", b.appDashboard, b.appDashboard.list),
      copy: safe("bitable.appDashboard.copy", b.appDashboard, b.appDashboard.copy),
    },
    roles: {
      create: safe("bitable.appRole.create", b.appRole, b.appRole.create),
      list: safe("bitable.appRole.list", b.appRole, b.appRole.list),
      update: safe("bitable.appRole.update", b.appRole, b.appRole.update),
      delete: safe("bitable.appRole.delete", b.appRole, b.appRole.delete),
      listMembers: safe("bitable.appRoleMember.list", b.appRoleMember, b.appRoleMember.list),
      createMember: safe("bitable.appRoleMember.create", b.appRoleMember, b.appRoleMember.create),
      batchCreateMembers: safe("bitable.appRoleMember.batchCreate", b.appRoleMember, b.appRoleMember.batchCreate),
      deleteMember: safe("bitable.appRoleMember.delete", b.appRoleMember, b.appRoleMember.delete),
      batchDeleteMembers: safe("bitable.appRoleMember.batchDelete", b.appRoleMember, b.appRoleMember.batchDelete),
    },
    workflows: {
      list: safe("bitable.appWorkflow.list", b.appWorkflow, b.appWorkflow.list),
      update: safe("bitable.appWorkflow.update", b.appWorkflow, b.appWorkflow.update),
    },
    blockWorkflows: {
      list: safe("bitable.appBlockWorkflow.list", b.appBlockWorkflow, b.appBlockWorkflow.list),
    },
  };
}

/**
 * Supporting Drive media operations used by Bitable attachment fields.
 * These are Drive APIs, not counted as Bitable endpoints in API_COVERAGE.md.
 */
export function createBitableAttachmentMethods(client: lark.Client) {
  const media = client.drive.media;

  return {
    upload: safe("drive.media.uploadAll", media, media.uploadAll),
    prepareUpload: safe("drive.media.uploadPrepare", media, media.uploadPrepare),
    uploadPart: safe("drive.media.uploadPart", media, media.uploadPart),
    finishUpload: safe("drive.media.uploadFinish", media, media.uploadFinish),
    download: safe("drive.media.download", media, media.download),
    batchGetTmpDownloadUrl: safe(
      "drive.media.batchGetTmpDownloadUrl",
      media,
      media.batchGetTmpDownloadUrl,
    ),
  };
}

export type BitableMethods = ReturnType<typeof createBitableMethods>;
export type BitableAttachmentMethods = ReturnType<typeof createBitableAttachmentMethods>;
