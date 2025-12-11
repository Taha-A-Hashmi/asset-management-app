import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import AddAssetForm from '../components/AddAssetForm';
import AssetTable from '../components/AssetTable';
import StatsCard from '../components/StatsCard';
import StatusChart from '../components/StatusChart';
import { createAsset, deleteAsset, getAssets, updateAsset } from '../services/api';

export default function Dashboard() {
  const [assets, setAssets] = useState([]);
  const [stats, setStats] = useState({ total: 0, in_stock: 0, out_stock: 0 });
  const [loading, setLoading] = useState(true);

  const fetchAssets = async () => {
    try {
      const data = await getAssets();
      setAssets(data.assets);
      setStats(data.stats);
    } catch {
      toast.error('Failed to load assets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssets();
  }, []);

  const handleAddAsset = async (formData) => {
    const toastId = toast.loading('Adding asset...');
    try {
      await createAsset(formData);
      toast.success('Asset added successfully!', { id: toastId });
      fetchAssets();
    } catch {
      toast.error('Failed to add asset', { id: toastId });
    }
  };

  const handleCheckout = async (id, location) => {
    await toast.promise(updateAsset(id, { status: 'Out', location }), {
      loading: 'Checking out...',
      success: `Sent to ${location}`,
      error: 'Checkout failed',
    });
    fetchAssets();
  };

  const handleCheckin = async (id) => {
    await toast.promise(updateAsset(id, { status: 'In', location: 'Warehouse' }), {
      loading: 'Returning asset...',
      success: 'Asset returned to warehouse',
      error: 'Check-in failed',
    });
    fetchAssets();
  };

  const handleDelete = (id) => {
    toast(
      (t) => (
        <div className="flex items-center gap-3">
          <span>Delete this asset?</span>
          <button
            onClick={() => {
              toast.dismiss(t.id);
              confirmDelete(id);
            }}
            className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
          >
            Delete
          </button>
          <button
            onClick={() => toast.dismiss(t.id)}
            className="text-gray-600 px-3 py-1 hover:bg-gray-100 rounded text-sm"
          >
            Cancel
          </button>
        </div>
      ),
      { duration: 5000 }
    );
  };

  const confirmDelete = async (id) => {
    await toast.promise(deleteAsset(id), {
      loading: 'Deleting...',
      success: 'Asset deleted',
      error: 'Failed to delete',
    });
    fetchAssets();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatsCard title="Total Assets" value={stats.total} color="blue" />
        <StatsCard title="In Stock" value={stats.in_stock} color="green" />
        <StatsCard title="On Demo" value={stats.out_stock} color="yellow" />
      </div>

      {/* Chart and Form */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <StatusChart inStock={stats.in_stock} outStock={stats.out_stock} />
        <AddAssetForm onSubmit={handleAddAsset} />
      </div>

      {/* Asset Table */}
      <AssetTable
        assets={assets}
        onCheckout={handleCheckout}
        onCheckin={handleCheckin}
        onDelete={handleDelete}
      />
    </div>
  );
}
